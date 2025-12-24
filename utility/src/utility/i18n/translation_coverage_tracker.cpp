#include <voltron/utility/i18n/translation_coverage_tracker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::i18n {

TranslationCoverageTracker& TranslationCoverageTracker::instance() {
    static TranslationCoverageTracker instance;
    return instance;
}

void TranslationCoverageTracker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[TranslationCoverageTracker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void TranslationCoverageTracker::shutdown() {
    enabled_ = false;
    std::cout << "[TranslationCoverageTracker] Shutdown\n";
}

bool TranslationCoverageTracker::isEnabled() const {
    return enabled_;
}

void TranslationCoverageTracker::enable() {
    enabled_ = true;
}

void TranslationCoverageTracker::disable() {
    enabled_ = false;
}

std::string TranslationCoverageTracker::getStatus() const {
    std::ostringstream oss;
    oss << "TranslationCoverageTracker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void TranslationCoverageTracker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::i18n
