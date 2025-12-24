#include <voltron/utility/plugin/dll_load_tracker.h>
#include <iostream>

namespace voltron::utility::plugin {

DllLoadTracker& DllLoadTracker::instance() {
    static DllLoadTracker instance;
    return instance;
}

void DllLoadTracker::initialize() {
    enabled_ = true;
}

void DllLoadTracker::shutdown() {
    enabled_ = false;
}

bool DllLoadTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::plugin
