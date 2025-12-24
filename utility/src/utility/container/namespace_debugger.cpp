#include <voltron/utility/container/namespace_debugger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::container {

NamespaceDebugger& NamespaceDebugger::instance() {
    static NamespaceDebugger instance;
    return instance;
}

void NamespaceDebugger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[NamespaceDebugger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void NamespaceDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[NamespaceDebugger] Shutdown\n";
}

bool NamespaceDebugger::isEnabled() const {
    return enabled_;
}

void NamespaceDebugger::enable() {
    enabled_ = true;
}

void NamespaceDebugger::disable() {
    enabled_ = false;
}

std::string NamespaceDebugger::getStatus() const {
    std::ostringstream oss;
    oss << "NamespaceDebugger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void NamespaceDebugger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::container
