#include "kd_tree.hpp"

#include <algorithm>
#include <atomic>
#include <functional>
#include <future>
#include <numeric>
#include <stdexcept>

namespace chamfer {

std::vector<KDNodeGPU> build_kd_tree(const float* points, int64_t num_points, int64_t dims) {
    if (num_points <= 0) {
        throw std::invalid_argument("build_kd_tree: num_points must be positive");
    }
    if (dims <= 0) {
        throw std::invalid_argument("build_kd_tree: dims must be positive");
    }

    std::vector<int> order(num_points);
    std::iota(order.begin(), order.end(), 0);

    std::vector<KDNodeGPU> gpu_nodes(static_cast<size_t>(num_points));
    std::atomic<int> next_index{0};

    const int dims_int = static_cast<int>(dims);
    const int max_parallel_depth = 2;
    const int parallel_threshold = 2048;

    std::function<int(int, int, int)> build = [&](int start, int end, int depth) -> int {
        if (start >= end) {
            return -1;
        }

        int axis = depth % dims_int;
        int mid = (start + end) / 2;

        auto comparator = [points, dims_int, axis, &order](int lhs, int rhs) {
            float l = points[static_cast<int64_t>(lhs) * dims_int + axis];
            float r = points[static_cast<int64_t>(rhs) * dims_int + axis];
            if (l == r) {
                return lhs < rhs;
            }
            return l < r;
        };

        std::nth_element(order.begin() + start, order.begin() + mid, order.begin() + end, comparator);

        int current = next_index.fetch_add(1, std::memory_order_relaxed);
        KDNodeGPU& node = gpu_nodes[static_cast<size_t>(current)];
        node.point_index = order[mid];
        node.split_dim = axis;
        node.split_value = points[static_cast<int64_t>(node.point_index) * dims_int + axis];
        node.pad0 = 0.0f;
        node.pad1 = 0.0f;
        node.pad2 = 0.0f;

        const bool parallel = depth < max_parallel_depth && (end - start) > parallel_threshold;

        int left_index;
        int right_index;
        if (parallel) {
            auto future_left = std::async(std::launch::async, [&]() {
                return build(start, mid, depth + 1);
            });
            right_index = build(mid + 1, end, depth + 1);
            left_index = future_left.get();
        } else {
            left_index = build(start, mid, depth + 1);
            right_index = build(mid + 1, end, depth + 1);
        }

        node.left = left_index;
        node.right = right_index;
        return current;
    };

    int root_index = build(0, static_cast<int>(num_points), 0);
    (void)root_index;

    gpu_nodes.resize(static_cast<size_t>(next_index.load(std::memory_order_relaxed)));

    return gpu_nodes;
}

}  // namespace chamfer
