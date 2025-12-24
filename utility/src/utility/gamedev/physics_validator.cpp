#include <voltron/utility/gamedev/physics_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::gamedev {

PhysicsValidator& PhysicsValidator::instance() {
    static PhysicsValidator instance;
    return instance;
}

void PhysicsValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PhysicsValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PhysicsValidator::shutdown() {
    enabled_ = false;
    std::cout << "[PhysicsValidator] Shutdown\n";
}

bool PhysicsValidator::isEnabled() const {
    return enabled_;
}

void PhysicsValidator::enable() {
    enabled_ = true;
}

void PhysicsValidator::disable() {
    enabled_ = false;
}

std::string PhysicsValidator::getStatus() const {
    std::ostringstream oss;
    oss << "PhysicsValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PhysicsValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::gamedev
