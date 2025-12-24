#include <voltron/utility/interop/marshalling_debugger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::interop {

MarshallingDebugger& MarshallingDebugger::instance() {
    static MarshallingDebugger instance;
    return instance;
}

void MarshallingDebugger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[MarshallingDebugger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void MarshallingDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[MarshallingDebugger] Shutdown\n";
}

bool MarshallingDebugger::isEnabled() const {
    return enabled_;
}

void MarshallingDebugger::enable() {
    enabled_ = true;
}

void MarshallingDebugger::disable() {
    enabled_ = false;
}

std::string MarshallingDebugger::getStatus() const {
    std::ostringstream oss;
    oss << "MarshallingDebugger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void MarshallingDebugger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::interop
