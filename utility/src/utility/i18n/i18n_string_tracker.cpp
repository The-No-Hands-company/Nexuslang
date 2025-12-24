#include <voltron/utility/i18n/i18n_string_tracker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::i18n {

I18nStringTracker& I18nStringTracker::instance() {
    static I18nStringTracker instance;
    return instance;
}

void I18nStringTracker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[I18nStringTracker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void I18nStringTracker::shutdown() {
    enabled_ = false;
    std::cout << "[I18nStringTracker] Shutdown\n";
}

bool I18nStringTracker::isEnabled() const {
    return enabled_;
}

void I18nStringTracker::enable() {
    enabled_ = true;
}

void I18nStringTracker::disable() {
    enabled_ = false;
}

std::string I18nStringTracker::getStatus() const {
    std::ostringstream oss;
    oss << "I18nStringTracker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void I18nStringTracker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::i18n
