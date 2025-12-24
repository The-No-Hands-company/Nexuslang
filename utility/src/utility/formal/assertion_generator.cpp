#include <voltron/utility/formal/assertion_generator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::formal {

AssertionGenerator& AssertionGenerator::instance() {
    static AssertionGenerator instance;
    return instance;
}

void AssertionGenerator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AssertionGenerator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AssertionGenerator::shutdown() {
    enabled_ = false;
    std::cout << "[AssertionGenerator] Shutdown\n";
}

bool AssertionGenerator::isEnabled() const {
    return enabled_;
}

void AssertionGenerator::enable() {
    enabled_ = true;
}

void AssertionGenerator::disable() {
    enabled_ = false;
}

std::string AssertionGenerator::getStatus() const {
    std::ostringstream oss;
    oss << "AssertionGenerator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AssertionGenerator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::formal
