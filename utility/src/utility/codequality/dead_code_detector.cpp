#include <voltron/utility/codequality/dead_code_detector.h>
#include <iostream>

namespace voltron::utility::codequality {

DeadCodeDetector& DeadCodeDetector::instance() {
    static DeadCodeDetector instance;
    return instance;
}

void DeadCodeDetector::initialize() {
    enabled_ = true;
}

void DeadCodeDetector::shutdown() {
    enabled_ = false;
}

bool DeadCodeDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::codequality
