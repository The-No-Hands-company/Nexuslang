#include <voltron/utility/protocol/timeout_debugger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::protocol {

TimeoutDebugger& TimeoutDebugger::instance() {
    static TimeoutDebugger instance;
    return instance;
}

void TimeoutDebugger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[TimeoutDebugger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void TimeoutDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[TimeoutDebugger] Shutdown\n";
}

bool TimeoutDebugger::isEnabled() const {
    return enabled_;
}

void TimeoutDebugger::enable() {
    enabled_ = true;
}

void TimeoutDebugger::disable() {
    enabled_ = false;
}

std::string TimeoutDebugger::getStatus() const {
    std::ostringstream oss;
    oss << "TimeoutDebugger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void TimeoutDebugger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::protocol
