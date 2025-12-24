#include <voltron/utility/embedded/priority_inversion_detector.h>
#include <iostream>

namespace voltron::utility::embedded {

PriorityInversionDetector& PriorityInversionDetector::instance() {
    static PriorityInversionDetector instance;
    return instance;
}

void PriorityInversionDetector::initialize() {
    enabled_ = true;
}

void PriorityInversionDetector::shutdown() {
    enabled_ = false;
}

bool PriorityInversionDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::embedded
