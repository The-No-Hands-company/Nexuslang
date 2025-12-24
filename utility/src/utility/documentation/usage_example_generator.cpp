#include <voltron/utility/documentation/usage_example_generator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::documentation {

UsageExampleGenerator& UsageExampleGenerator::instance() {
    static UsageExampleGenerator instance;
    return instance;
}

void UsageExampleGenerator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[UsageExampleGenerator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void UsageExampleGenerator::shutdown() {
    enabled_ = false;
    std::cout << "[UsageExampleGenerator] Shutdown\n";
}

bool UsageExampleGenerator::isEnabled() const {
    return enabled_;
}

void UsageExampleGenerator::enable() {
    enabled_ = true;
}

void UsageExampleGenerator::disable() {
    enabled_ = false;
}

std::string UsageExampleGenerator::getStatus() const {
    std::ostringstream oss;
    oss << "UsageExampleGenerator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void UsageExampleGenerator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::documentation
