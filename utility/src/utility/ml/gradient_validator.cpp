#include <voltron/utility/ml/gradient_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::ml {

GradientValidator& GradientValidator::instance() {
    static GradientValidator instance;
    return instance;
}

void GradientValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[GradientValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void GradientValidator::shutdown() {
    enabled_ = false;
    std::cout << "[GradientValidator] Shutdown\n";
}

bool GradientValidator::isEnabled() const {
    return enabled_;
}

void GradientValidator::enable() {
    enabled_ = true;
}

void GradientValidator::disable() {
    enabled_ = false;
}

std::string GradientValidator::getStatus() const {
    std::ostringstream oss;
    oss << "GradientValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void GradientValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::ml
