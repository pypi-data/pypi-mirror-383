#import <Foundation/Foundation.h>
#import <Metal/Metal.h>

#include <nanobind/nanobind.h>
#include <torch/extension.h>
#include <torch/csrc/autograd/python_variable.h>
#include <ATen/mps/MPSStream.h>

#include <algorithm>
#include <cstring>
#include <limits>
#include <mutex>
#include <stdexcept>
#include <string>
#include <vector>
#include <mach/mach_time.h>

#include "kd_tree.hpp"

namespace nb = nanobind;

namespace {

inline id<MTLBuffer> tensor_to_mtl_buffer(const at::Tensor& tensor) {
    return (__bridge id<MTLBuffer>)(tensor.storage().data());
}

struct TimebaseInfo {
    uint64_t numer = 0;
    uint64_t denom = 0;
    TimebaseInfo() {
        mach_timebase_info_data_t info;
        mach_timebase_info(&info);
        numer = info.numer;
        denom = info.denom;
    }
    double to_millis(uint64_t delta) const {
        double nanoseconds = static_cast<double>(delta) * static_cast<double>(numer) / static_cast<double>(denom);
        return nanoseconds / 1e6;
    }
};

const TimebaseInfo& timebase() {
    static TimebaseInfo info;
    return info;
}

bool should_profile() {
    static bool initialized = false;
    static bool enabled = false;
    if (!initialized) {
        const char* env = std::getenv("CHAMFER_PROFILE");
        enabled = env && std::strlen(env) > 0;
        initialized = true;
    }
    return enabled;
}

struct ScopedTimer {
    const TimebaseInfo& info;
    uint64_t start;
    std::string label;
    bool enabled;
    ScopedTimer(const TimebaseInfo& info, std::string lbl, bool en)
        : info(info), start(en ? mach_absolute_time() : 0), label(std::move(lbl)), enabled(en) {}
    ~ScopedTimer() {
        if (enabled) {
            uint64_t end = mach_absolute_time();
            double ms = info.to_millis(end - start);
            fprintf(stderr, "[chamfer] %s: %.3f ms\n", label.c_str(), ms);
        }
    }
};

constexpr const char* kMetalSource = R"(using namespace metal;

struct KDNode {
    int left;
    int right;
    int point_index;
    int split_dim;
    float split_value;
    float pad0;
    float pad1;
    float pad2;
};

inline float distance_squared(const device float* a,
                              const device float* b,
                              int dims) {
    float acc = 0.0f;
    for (int i = 0; i < dims; ++i) {
        float diff = a[i] - b[i];
        acc += diff * diff;
    }
    return acc;
}

kernel void kd_query(device const float* ref_points [[buffer(0)]],
                     device const KDNode* nodes [[buffer(1)]],
                     constant int& num_nodes [[buffer(2)]],
                     constant int& dims [[buffer(3)]],
                     device const float* queries [[buffer(4)]],
                     constant int& num_queries [[buffer(5)]],
                     device int* out_indices [[buffer(6)]],
                     device float* out_distances [[buffer(7)]],
                     uint gid [[thread_position_in_grid]]) {
    if (gid >= static_cast<uint>(num_queries)) {
        return;
    }

    constexpr int STACK_CAP = 128;
    int stack[STACK_CAP];
    int stack_size = 0;

    if (num_nodes > 0) {
        stack[stack_size++] = 0;
    }

    device const float* query = queries + static_cast<size_t>(gid) * static_cast<size_t>(dims);

    float best_dist = INFINITY;
    int best_index = -1;

    while (stack_size > 0) {
        int node_idx = stack[--stack_size];
        if (node_idx < 0 || node_idx >= num_nodes) {
            continue;
        }

        KDNode node = nodes[node_idx];
        int point_idx = node.point_index;
        device const float* point = ref_points + static_cast<size_t>(point_idx) * static_cast<size_t>(dims);

        float dist = distance_squared(query, point, dims);
        if (dist < best_dist) {
            best_dist = dist;
            best_index = point_idx;
        }

        int left = node.left;
        int right = node.right;
        if (left < 0 && right < 0) {
            continue;
        }

        float diff = query[node.split_dim] - node.split_value;
        int near_child = diff <= 0.0f ? left : right;
        int far_child = diff <= 0.0f ? right : left;

        if (far_child >= 0 && stack_size < STACK_CAP && diff * diff < best_dist) {
            stack[stack_size++] = far_child;
        }
        if (near_child >= 0 && stack_size < STACK_CAP) {
            stack[stack_size++] = near_child;
        }
    }

    if (best_index < 0) {
        best_dist = 0.0f;
    }

    out_indices[gid] = best_index;
    out_distances[gid] = best_dist;
}
)";

struct MetalContext {
    id<MTLDevice> device = nil;
    id<MTLCommandQueue> queue = nil;
    id<MTLLibrary> library = nil;
    id<MTLComputePipelineState> pipeline = nil;
    bool initialized = false;
    bool attempted = false;
    std::string error_message;
};

MetalContext& get_context() {
    static MetalContext ctx;
    return ctx;
}

void initialize_metal_once() {
    auto& ctx = get_context();
    static std::once_flag once_flag;
    std::call_once(once_flag, [&ctx]() {
        ctx.attempted = true;
        ctx.device = MTLCreateSystemDefaultDevice();
        if (!ctx.device) {
            ctx.error_message = "No Metal-capable device available for MPS";
            return;
        }
        ctx.queue = [ctx.device newCommandQueue];
        if (!ctx.queue) {
            ctx.error_message = "Failed to create Metal command queue";
            return;
        }

        NSError* error = nil;
        NSString* source = [[NSString alloc] initWithUTF8String:kMetalSource];
        MTLCompileOptions* options = [[MTLCompileOptions alloc] init];
        options.fastMathEnabled = YES;

        ctx.library = [ctx.device newLibraryWithSource:source options:options error:&error];
        if (!ctx.library) {
            std::string message = "Failed to compile Metal library: ";
            if (error) {
                message += [[error localizedDescription] UTF8String];
            }
            ctx.error_message = message;
            return;
        }

        id<MTLFunction> function = [ctx.library newFunctionWithName:@"kd_query"];
        if (!function) {
            ctx.error_message = "Failed to load kd_query function from Metal library";
            return;
        }

        ctx.pipeline = [ctx.device newComputePipelineStateWithFunction:function error:&error];
        if (!ctx.pipeline) {
            std::string message = "Failed to create pipeline state: ";
            if (error) {
                message += [[error localizedDescription] UTF8String];
            }
            ctx.error_message = message;
            return;
        }

        ctx.initialized = true;
    });
}

void ensure_initialized() {
    initialize_metal_once();
    auto& ctx = get_context();

    if (!ctx.initialized) {
        if (!ctx.error_message.empty()) {
            throw std::runtime_error(ctx.error_message);
        }
        throw std::runtime_error("Metal context failed to initialize");
    }
}

const at::Tensor& tensor_from_nb(nb::handle h) {
    if (!THPVariable_Check(h.ptr())) {
        throw nb::type_error("expected a torch.Tensor");
    }
    return THPVariable_Unpack(h.ptr());
}

nb::tuple kd_tree_query(nb::handle query_handle, nb::handle reference_handle) {
    torch::NoGradGuard guard;

    const bool profile = should_profile();
    const TimebaseInfo& tinfo = timebase();
    ScopedTimer total_timer(tinfo, "kd_query_total", profile);

    const at::Tensor& query_in = tensor_from_nb(query_handle);
    const at::Tensor& reference_in = tensor_from_nb(reference_handle);

    if (query_in.dim() != 2) {
        throw std::invalid_argument("query tensor must be 2D [N, K]");
    }
    if (reference_in.dim() != 2) {
        throw std::invalid_argument("reference tensor must be 2D [M, K]");
    }
    if (query_in.size(1) != reference_in.size(1)) {
        throw std::invalid_argument("query and reference tensors must have the same dimensionality");
    }

    if (!query_in.device().is_mps() || !reference_in.device().is_mps()) {
        throw std::invalid_argument("kd_query expects query and reference tensors on MPS device");
    }
    if (query_in.scalar_type() != at::kFloat || reference_in.scalar_type() != at::kFloat) {
        throw std::invalid_argument("kd_query expects float32 tensors");
    }

    int64_t dims = query_in.size(1);
    int64_t num_query = query_in.size(0);
    int64_t num_reference = reference_in.size(0);

    if (num_reference == 0) {
        throw std::invalid_argument("reference set must contain at least one point");
    }

    at::Tensor query_mps = query_in.contiguous();
    at::Tensor reference_mps = reference_in.contiguous();

    at::mps::getCurrentMPSStream()->synchronize(at::mps::SyncType::COMMIT_AND_WAIT);

    ensure_initialized();
    auto& ctx = get_context();

    at::Tensor reference_cpu;
    {
        ScopedTimer cpu_copy_timer(tinfo, "kd_query_copy_to_cpu", profile);
        reference_cpu = reference_mps.to(at::kCPU).contiguous();
    }

    std::vector<chamfer::KDNodeGPU> nodes;
    {
        ScopedTimer build_timer(tinfo, "kd_tree_build", profile);
        nodes = chamfer::build_kd_tree(reference_cpu.data_ptr<float>(), num_reference, dims);
    }
    if (nodes.empty()) {
        throw std::runtime_error("Failed to build kd-tree");
    }

    NSUInteger node_bytes = static_cast<NSUInteger>(nodes.size() * sizeof(chamfer::KDNodeGPU));
    id<MTLBuffer> node_buffer = [ctx.device newBufferWithBytes:nodes.data()
                                                        length:node_bytes
                                                       options:MTLResourceStorageModeShared];
    if (!node_buffer) {
        throw std::runtime_error("Failed to allocate node buffers");
    }

    auto indices_tensor = torch::empty({num_query}, torch::TensorOptions().dtype(torch::kInt32).device(torch::kMPS));
    auto distances_tensor = torch::empty({num_query}, torch::TensorOptions().dtype(torch::kFloat).device(torch::kMPS));

    id<MTLBuffer> points_buffer = tensor_to_mtl_buffer(reference_mps);
    id<MTLBuffer> query_buffer = tensor_to_mtl_buffer(query_mps);
    id<MTLBuffer> indices_buffer = tensor_to_mtl_buffer(indices_tensor);
    id<MTLBuffer> distances_buffer = tensor_to_mtl_buffer(distances_tensor);

    if (!points_buffer || !query_buffer || !node_buffer || !indices_buffer || !distances_buffer) {
        throw std::runtime_error("Failed to allocate Metal buffers");
    }

    id<MTLCommandBuffer> command_buffer = [ctx.queue commandBuffer];
    if (!command_buffer) {
        throw std::runtime_error("Failed to create Metal command buffer");
    }
    id<MTLComputeCommandEncoder> encoder = [command_buffer computeCommandEncoder];
    [encoder setComputePipelineState:ctx.pipeline];

    int num_nodes = static_cast<int>(nodes.size());
    int dims_i = static_cast<int>(dims);
    int num_query_i = static_cast<int>(num_query);

    NSUInteger points_offset = static_cast<NSUInteger>(reference_mps.storage_offset() * reference_mps.element_size());
    NSUInteger query_offset = static_cast<NSUInteger>(query_mps.storage_offset() * query_mps.element_size());
    NSUInteger indices_offset = static_cast<NSUInteger>(indices_tensor.storage_offset() * indices_tensor.element_size());
    NSUInteger distances_offset = static_cast<NSUInteger>(distances_tensor.storage_offset() * distances_tensor.element_size());

    [encoder setBuffer:points_buffer offset:points_offset atIndex:0];
    [encoder setBuffer:node_buffer offset:0 atIndex:1];
    [encoder setBytes:&num_nodes length:sizeof(int) atIndex:2];
    [encoder setBytes:&dims_i length:sizeof(int) atIndex:3];
    [encoder setBuffer:query_buffer offset:query_offset atIndex:4];
    [encoder setBytes:&num_query_i length:sizeof(int) atIndex:5];
    [encoder setBuffer:indices_buffer offset:indices_offset atIndex:6];
    [encoder setBuffer:distances_buffer offset:distances_offset atIndex:7];

    NSUInteger max_threads = ctx.pipeline.maxTotalThreadsPerThreadgroup;
    if (max_threads == 0) {
        max_threads = 64;
    }
    NSUInteger threadgroup_size = std::min<NSUInteger>(max_threads, 256);
    MTLSize threads_per_threadgroup = MTLSizeMake(threadgroup_size, 1, 1);
    NSUInteger grid_threads = static_cast<NSUInteger>(num_query);
    NSUInteger groups = (grid_threads + threadgroup_size - 1) / threadgroup_size;
    MTLSize threads_per_grid = MTLSizeMake(groups * threadgroup_size, 1, 1);
    {
        ScopedTimer dispatch_timer(tinfo, "kd_query_dispatch", profile);
        [encoder dispatchThreads:threads_per_grid threadsPerThreadgroup:threads_per_threadgroup];
        [encoder endEncoding];
        [command_buffer commit];
    }

    {
        ScopedTimer wait_timer(tinfo, "kd_query_wait", profile);
        [command_buffer waitUntilCompleted];
    }

    PyObject* indices_obj = THPVariable_Wrap(indices_tensor);
    PyObject* distances_obj = THPVariable_Wrap(distances_tensor);

    return nb::make_tuple(nb::steal<nb::object>(indices_obj), nb::steal<nb::object>(distances_obj));
}

nb::tuple kd_tree_query_cpu(nb::handle query_handle, nb::handle reference_handle) {
    torch::NoGradGuard guard;

    const at::Tensor& query_in = tensor_from_nb(query_handle);
    const at::Tensor& reference_in = tensor_from_nb(reference_handle);

    if (query_in.dim() != 2) {
        throw std::invalid_argument("query tensor must be 2D [N, K]");
    }
    if (reference_in.dim() != 2) {
        throw std::invalid_argument("reference tensor must be 2D [M, K]");
    }
    if (query_in.size(1) != reference_in.size(1)) {
        throw std::invalid_argument("query and reference tensors must have the same dimensionality");
    }

    int64_t dims = query_in.size(1);
    int64_t num_query = query_in.size(0);
    int64_t num_reference = reference_in.size(0);

    if (num_reference == 0) {
        throw std::invalid_argument("reference set must contain at least one point");
    }

    at::Tensor query_cpu = query_in;
    if (!query_cpu.device().is_cpu() || query_cpu.scalar_type() != at::kFloat || !query_cpu.is_contiguous()) {
        query_cpu = query_in.to(at::kCPU, at::kFloat).contiguous();
    }

    at::Tensor reference_cpu = reference_in;
    if (!reference_cpu.device().is_cpu() || reference_cpu.scalar_type() != at::kFloat || !reference_cpu.is_contiguous()) {
        reference_cpu = reference_in.to(at::kCPU, at::kFloat).contiguous();
    }

    auto nodes = chamfer::build_kd_tree(reference_cpu.data_ptr<float>(), num_reference, dims);
    if (nodes.empty()) {
        throw std::runtime_error("Failed to build kd-tree");
    }

    auto indices_tensor = torch::empty({num_query}, torch::dtype(torch::kInt32).device(torch::kCPU));
    auto distances_tensor = torch::empty({num_query}, torch::dtype(torch::kFloat).device(torch::kCPU));

    const float* query_ptr = query_cpu.data_ptr<float>();
    const float* reference_ptr = reference_cpu.data_ptr<float>();
    int32_t* index_ptr = indices_tensor.data_ptr<int32_t>();
    float* distance_ptr = distances_tensor.data_ptr<float>();

    std::vector<int> stack;
    stack.reserve(64);

    for (int64_t qi = 0; qi < num_query; ++qi) {
        const float* query = query_ptr + qi * dims;
        float best_dist = std::numeric_limits<float>::infinity();
        int best_index = -1;

        stack.clear();
        if (!nodes.empty()) {
            stack.push_back(0);
        }

        while (!stack.empty()) {
            int node_idx = stack.back();
            stack.pop_back();
            if (node_idx < 0 || node_idx >= static_cast<int>(nodes.size())) {
                continue;
            }

            const auto& node = nodes[node_idx];
            int point_idx = node.point_index;
            const float* point = reference_ptr + static_cast<int64_t>(point_idx) * dims;

            float dist = 0.0f;
            for (int64_t d = 0; d < dims; ++d) {
                float diff = query[d] - point[d];
                dist += diff * diff;
            }

            if (dist < best_dist) {
                best_dist = dist;
                best_index = point_idx;
            }

            int left = node.left;
            int right = node.right;
            if (left < 0 && right < 0) {
                continue;
            }

            float diff = query[node.split_dim] - node.split_value;
            int near_child = diff <= 0.0f ? left : right;
            int far_child = diff <= 0.0f ? right : left;

            if (far_child >= 0 && diff * diff < best_dist) {
                stack.push_back(far_child);
            }
            if (near_child >= 0) {
                stack.push_back(near_child);
            }
        }

        if (best_index < 0) {
            best_dist = 0.0f;
            best_index = 0;
        }

        index_ptr[qi] = best_index;
        distance_ptr[qi] = best_dist;
    }

    PyObject* indices_obj = THPVariable_Wrap(indices_tensor);
    PyObject* distances_obj = THPVariable_Wrap(distances_tensor);

    return nb::make_tuple(nb::steal<nb::object>(indices_obj), nb::steal<nb::object>(distances_obj));
}

}  // namespace

NB_MODULE(chamfer_ext, m) {
    m.def("kd_query", &kd_tree_query, "KD-tree nearest neighbour query using Metal");
    m.def("kd_query_cpu", &kd_tree_query_cpu, "KD-tree nearest neighbour query on CPU");
}
