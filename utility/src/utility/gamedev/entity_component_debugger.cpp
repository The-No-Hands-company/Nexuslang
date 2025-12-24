#include <voltron/utility/gamedev/entity_component_debugger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::gamedev {

EntityComponentDebugger& EntityComponentDebugger::instance() {
    static EntityComponentDebugger instance;
    return instance;
}

void EntityComponentDebugger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[EntityComponentDebugger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void EntityComponentDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[EntityComponentDebugger] Shutdown\n";
}

bool EntityComponentDebugger::isEnabled() const {
    return enabled_;
}

void EntityComponentDebugger::enable() {
    enabled_ = true;
}

void EntityComponentDebugger::disable() {
    enabled_ = false;
}

std::string EntityComponentDebugger::getStatus() const {
    std::ostringstream oss;
    oss << "EntityComponentDebugger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void EntityComponentDebugger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::gamedev
