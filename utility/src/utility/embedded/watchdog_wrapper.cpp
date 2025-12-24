#include <voltron/utility/embedded/watchdog_wrapper.h>
#include <iostream>

namespace voltron::utility::embedded {

WatchdogWrapper& WatchdogWrapper::instance() {
    static WatchdogWrapper instance;
    return instance;
}

void WatchdogWrapper::initialize() {
    enabled_ = true;
}

void WatchdogWrapper::shutdown() {
    enabled_ = false;
}

bool WatchdogWrapper::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::embedded
