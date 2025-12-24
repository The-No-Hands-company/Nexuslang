#include <voltron/utility/codequality/cyclomatic_complexity_tracker.h>
#include <iostream>

namespace voltron::utility::codequality {

CyclomaticComplexityTracker& CyclomaticComplexityTracker::instance() {
    static CyclomaticComplexityTracker instance;
    return instance;
}

void CyclomaticComplexityTracker::initialize() {
    enabled_ = true;
}

void CyclomaticComplexityTracker::shutdown() {
    enabled_ = false;
}

bool CyclomaticComplexityTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::codequality
