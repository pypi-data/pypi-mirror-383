#pragma once

#include <vector>
#include <cstddef>

namespace chamfer {

struct KDNodeGPU {
    int left;
    int right;
    int point_index;
    int split_dim;
    float split_value;
    float pad0;
    float pad1;
    float pad2;
};

std::vector<KDNodeGPU> build_kd_tree(const float* points, int64_t num_points, int64_t dims);

}

