#include <voltron/utility/safety/redundancy_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::safety {

RedundancyValidator& RedundancyValidator::instance() {
    static RedundancyValidator instance;
    return instance;
}

void RedundancyValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[RedundancyValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void RedundancyValidator::shutdown() {
    enabled_ = false;
    std::cout << "[RedundancyValidator] Shutdown\n";
}

bool RedundancyValidator::isEnabled() const {
    return enabled_;
}

void RedundancyValidator::enable() {
    enabled_ = true;
}

void RedundancyValidator::disable() {
    enabled_ = false;
}

std::string RedundancyValidator::getStatus() const {
    std::ostringstream oss;
    oss << "RedundancyValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void RedundancyValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::safety
