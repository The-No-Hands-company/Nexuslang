#include <voltron/utility/system/signal_safe_utilities.h>
#include <iostream>

namespace voltron::utility::system {

SignalSafeUtilities& SignalSafeUtilities::instance() {
    static SignalSafeUtilities instance;
    return instance;
}

void SignalSafeUtilities::initialize() {
    enabled_ = true;
    std::cout << "[SignalSafeUtilities] Initialized\n";
}

void SignalSafeUtilities::shutdown() {
    enabled_ = false;
    std::cout << "[SignalSafeUtilities] Shutdown\n";
}

bool SignalSafeUtilities::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::system
