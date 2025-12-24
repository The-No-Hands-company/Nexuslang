#include <voltron/utility/compiler/optimization_barrier.h>
#include <iostream>

namespace voltron::utility::compiler {

OptimizationBarrier& OptimizationBarrier::instance() {
    static OptimizationBarrier instance;
    return instance;
}

void OptimizationBarrier::initialize() {
    enabled_ = true;
    std::cout << "[OptimizationBarrier] Initialized\n";
}

void OptimizationBarrier::shutdown() {
    enabled_ = false;
    std::cout << "[OptimizationBarrier] Shutdown\n";
}

bool OptimizationBarrier::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::compiler
