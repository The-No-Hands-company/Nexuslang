#include <voltron/utility/hardware/sensor_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::hardware {

SensorValidator& SensorValidator::instance() {
    static SensorValidator instance;
    return instance;
}

void SensorValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[SensorValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void SensorValidator::shutdown() {
    enabled_ = false;
    std::cout << "[SensorValidator] Shutdown\n";
}

bool SensorValidator::isEnabled() const {
    return enabled_;
}

void SensorValidator::enable() {
    enabled_ = true;
}

void SensorValidator::disable() {
    enabled_ = false;
}

std::string SensorValidator::getStatus() const {
    std::ostringstream oss;
    oss << "SensorValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void SensorValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::hardware
