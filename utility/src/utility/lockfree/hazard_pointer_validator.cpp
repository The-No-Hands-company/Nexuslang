#include <voltron/utility/lockfree/hazard_pointer_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::lockfree {

HazardPointerValidator& HazardPointerValidator::instance() {
    static HazardPointerValidator instance;
    return instance;
}

void HazardPointerValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[HazardPointerValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void HazardPointerValidator::shutdown() {
    enabled_ = false;
    std::cout << "[HazardPointerValidator] Shutdown\n";
}

bool HazardPointerValidator::isEnabled() const {
    return enabled_;
}

void HazardPointerValidator::enable() {
    enabled_ = true;
}

void HazardPointerValidator::disable() {
    enabled_ = false;
}

std::string HazardPointerValidator::getStatus() const {
    std::ostringstream oss;
    oss << "HazardPointerValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void HazardPointerValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::lockfree
