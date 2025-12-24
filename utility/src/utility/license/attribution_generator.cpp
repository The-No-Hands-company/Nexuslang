#include <voltron/utility/license/attribution_generator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::license {

AttributionGenerator& AttributionGenerator::instance() {
    static AttributionGenerator instance;
    return instance;
}

void AttributionGenerator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AttributionGenerator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AttributionGenerator::shutdown() {
    enabled_ = false;
    std::cout << "[AttributionGenerator] Shutdown\n";
}

bool AttributionGenerator::isEnabled() const {
    return enabled_;
}

void AttributionGenerator::enable() {
    enabled_ = true;
}

void AttributionGenerator::disable() {
    enabled_ = false;
}

std::string AttributionGenerator::getStatus() const {
    std::ostringstream oss;
    oss << "AttributionGenerator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AttributionGenerator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::license
