#include <voltron/utility/network/retry_policy_debugger.h>
#include <iostream>

namespace voltron::utility::network {

RetryPolicyDebugger& RetryPolicyDebugger::instance() {
    static RetryPolicyDebugger instance;
    return instance;
}

void RetryPolicyDebugger::initialize() {
    enabled_ = true;
    std::cout << "[RetryPolicyDebugger] Initialized\n";
}

void RetryPolicyDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[RetryPolicyDebugger] Shutdown\n";
}

bool RetryPolicyDebugger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::network
