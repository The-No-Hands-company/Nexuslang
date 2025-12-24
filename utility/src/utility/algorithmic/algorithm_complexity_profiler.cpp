#include <voltron/utility/algorithmic/algorithm_complexity_profiler.h>
#include <iostream>

namespace voltron::utility::algorithmic {

AlgorithmComplexityProfiler& AlgorithmComplexityProfiler::instance() {
    static AlgorithmComplexityProfiler instance;
    return instance;
}

void AlgorithmComplexityProfiler::initialize() {
    enabled_ = true;
}

void AlgorithmComplexityProfiler::shutdown() {
    enabled_ = false;
}

bool AlgorithmComplexityProfiler::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::algorithmic
