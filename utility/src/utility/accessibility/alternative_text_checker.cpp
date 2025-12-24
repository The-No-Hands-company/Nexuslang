#include <voltron/utility/accessibility/alternative_text_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::accessibility {

AlternativeTextChecker& AlternativeTextChecker::instance() {
    static AlternativeTextChecker instance;
    return instance;
}

void AlternativeTextChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AlternativeTextChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AlternativeTextChecker::shutdown() {
    enabled_ = false;
    std::cout << "[AlternativeTextChecker] Shutdown\n";
}

bool AlternativeTextChecker::isEnabled() const {
    return enabled_;
}

void AlternativeTextChecker::enable() {
    enabled_ = true;
}

void AlternativeTextChecker::disable() {
    enabled_ = false;
}

std::string AlternativeTextChecker::getStatus() const {
    std::ostringstream oss;
    oss << "AlternativeTextChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AlternativeTextChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::accessibility
