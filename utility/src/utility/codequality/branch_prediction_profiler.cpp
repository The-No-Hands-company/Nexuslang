#include <voltron/utility/codequality/branch_prediction_profiler.h>
#include <iostream>

namespace voltron::utility::codequality {

BranchPredictionProfiler& BranchPredictionProfiler::instance() {
    static BranchPredictionProfiler instance;
    return instance;
}

void BranchPredictionProfiler::initialize() {
    enabled_ = true;
}

void BranchPredictionProfiler::shutdown() {
    enabled_ = false;
}

bool BranchPredictionProfiler::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::codequality
