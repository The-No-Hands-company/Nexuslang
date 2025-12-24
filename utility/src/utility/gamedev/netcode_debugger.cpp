#include <voltron/utility/gamedev/netcode_debugger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::gamedev {

NetcodeDebugger& NetcodeDebugger::instance() {
    static NetcodeDebugger instance;
    return instance;
}

void NetcodeDebugger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[NetcodeDebugger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void NetcodeDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[NetcodeDebugger] Shutdown\n";
}

bool NetcodeDebugger::isEnabled() const {
    return enabled_;
}

void NetcodeDebugger::enable() {
    enabled_ = true;
}

void NetcodeDebugger::disable() {
    enabled_ = false;
}

std::string NetcodeDebugger::getStatus() const {
    std::ostringstream oss;
    oss << "NetcodeDebugger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void NetcodeDebugger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::gamedev
