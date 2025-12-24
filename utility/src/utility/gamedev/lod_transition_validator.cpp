#include <voltron/utility/gamedev/lod_transition_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::gamedev {

LodTransitionValidator& LodTransitionValidator::instance() {
    static LodTransitionValidator instance;
    return instance;
}

void LodTransitionValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[LodTransitionValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void LodTransitionValidator::shutdown() {
    enabled_ = false;
    std::cout << "[LodTransitionValidator] Shutdown\n";
}

bool LodTransitionValidator::isEnabled() const {
    return enabled_;
}

void LodTransitionValidator::enable() {
    enabled_ = true;
}

void LodTransitionValidator::disable() {
    enabled_ = false;
}

std::string LodTransitionValidator::getStatus() const {
    std::ostringstream oss;
    oss << "LodTransitionValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void LodTransitionValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::gamedev
