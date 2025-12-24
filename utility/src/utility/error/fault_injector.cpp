#include <voltron/utility/error/fault_injector.h>
#include <iostream>

namespace voltron::utility::error {

FaultInjector& FaultInjector::instance() {
    static FaultInjector instance;
    return instance;
}

void FaultInjector::initialize() {
    enabled_ = true;
    std::cout << "[FaultInjector] Initialized\n";
}

void FaultInjector::shutdown() {
    enabled_ = false;
    std::cout << "[FaultInjector] Shutdown\n";
}

bool FaultInjector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::error
