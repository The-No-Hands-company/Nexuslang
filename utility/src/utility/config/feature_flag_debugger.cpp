#include <voltron/utility/config/feature_flag_debugger.h>
#include <iostream>

namespace voltron::utility::config {

FeatureFlagDebugger& FeatureFlagDebugger::instance() {
    static FeatureFlagDebugger instance;
    return instance;
}

void FeatureFlagDebugger::initialize() {
    enabled_ = true;
    std::cout << "[FeatureFlagDebugger] Initialized\n";
}

void FeatureFlagDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[FeatureFlagDebugger] Shutdown\n";
}

bool FeatureFlagDebugger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::config
