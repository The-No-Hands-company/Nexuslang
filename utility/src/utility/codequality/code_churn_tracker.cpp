#include <voltron/utility/codequality/code_churn_tracker.h>
#include <iostream>

namespace voltron::utility::codequality {

CodeChurnTracker& CodeChurnTracker::instance() {
    static CodeChurnTracker instance;
    return instance;
}

void CodeChurnTracker::initialize() {
    enabled_ = true;
}

void CodeChurnTracker::shutdown() {
    enabled_ = false;
}

bool CodeChurnTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::codequality
