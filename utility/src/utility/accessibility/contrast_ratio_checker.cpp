#include <voltron/utility/accessibility/contrast_ratio_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::accessibility {

ContrastRatioChecker& ContrastRatioChecker::instance() {
    static ContrastRatioChecker instance;
    return instance;
}

void ContrastRatioChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ContrastRatioChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ContrastRatioChecker::shutdown() {
    enabled_ = false;
    std::cout << "[ContrastRatioChecker] Shutdown\n";
}

bool ContrastRatioChecker::isEnabled() const {
    return enabled_;
}

void ContrastRatioChecker::enable() {
    enabled_ = true;
}

void ContrastRatioChecker::disable() {
    enabled_ = false;
}

std::string ContrastRatioChecker::getStatus() const {
    std::ostringstream oss;
    oss << "ContrastRatioChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ContrastRatioChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::accessibility
