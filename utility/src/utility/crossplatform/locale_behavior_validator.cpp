#include <voltron/utility/crossplatform/locale_behavior_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::crossplatform {

LocaleBehaviorValidator& LocaleBehaviorValidator::instance() {
    static LocaleBehaviorValidator instance;
    return instance;
}

void LocaleBehaviorValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[LocaleBehaviorValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void LocaleBehaviorValidator::shutdown() {
    enabled_ = false;
    std::cout << "[LocaleBehaviorValidator] Shutdown\n";
}

bool LocaleBehaviorValidator::isEnabled() const {
    return enabled_;
}

void LocaleBehaviorValidator::enable() {
    enabled_ = true;
}

void LocaleBehaviorValidator::disable() {
    enabled_ = false;
}

std::string LocaleBehaviorValidator::getStatus() const {
    std::ostringstream oss;
    oss << "LocaleBehaviorValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void LocaleBehaviorValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::crossplatform
