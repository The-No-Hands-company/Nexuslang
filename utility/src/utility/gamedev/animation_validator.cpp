#include <voltron/utility/gamedev/animation_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::gamedev {

AnimationValidator& AnimationValidator::instance() {
    static AnimationValidator instance;
    return instance;
}

void AnimationValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AnimationValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AnimationValidator::shutdown() {
    enabled_ = false;
    std::cout << "[AnimationValidator] Shutdown\n";
}

bool AnimationValidator::isEnabled() const {
    return enabled_;
}

void AnimationValidator::enable() {
    enabled_ = true;
}

void AnimationValidator::disable() {
    enabled_ = false;
}

std::string AnimationValidator::getStatus() const {
    std::ostringstream oss;
    oss << "AnimationValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AnimationValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::gamedev
