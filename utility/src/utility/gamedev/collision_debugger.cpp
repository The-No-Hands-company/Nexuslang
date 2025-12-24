#include <voltron/utility/gamedev/collision_debugger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::gamedev {

CollisionDebugger& CollisionDebugger::instance() {
    static CollisionDebugger instance;
    return instance;
}

void CollisionDebugger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CollisionDebugger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CollisionDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[CollisionDebugger] Shutdown\n";
}

bool CollisionDebugger::isEnabled() const {
    return enabled_;
}

void CollisionDebugger::enable() {
    enabled_ = true;
}

void CollisionDebugger::disable() {
    enabled_ = false;
}

std::string CollisionDebugger::getStatus() const {
    std::ostringstream oss;
    oss << "CollisionDebugger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CollisionDebugger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::gamedev
