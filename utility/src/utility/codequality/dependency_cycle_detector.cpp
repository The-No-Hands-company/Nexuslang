#include <voltron/utility/codequality/dependency_cycle_detector.h>
#include <iostream>

namespace voltron::utility::codequality {

DependencyCycleDetector& DependencyCycleDetector::instance() {
    static DependencyCycleDetector instance;
    return instance;
}

void DependencyCycleDetector::initialize() {
    enabled_ = true;
}

void DependencyCycleDetector::shutdown() {
    enabled_ = false;
}

bool DependencyCycleDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::codequality
