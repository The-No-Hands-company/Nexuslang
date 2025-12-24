#include <voltron/utility/crossplatform/line_ending_normalizer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::crossplatform {

LineEndingNormalizer& LineEndingNormalizer::instance() {
    static LineEndingNormalizer instance;
    return instance;
}

void LineEndingNormalizer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[LineEndingNormalizer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void LineEndingNormalizer::shutdown() {
    enabled_ = false;
    std::cout << "[LineEndingNormalizer] Shutdown\n";
}

bool LineEndingNormalizer::isEnabled() const {
    return enabled_;
}

void LineEndingNormalizer::enable() {
    enabled_ = true;
}

void LineEndingNormalizer::disable() {
    enabled_ = false;
}

std::string LineEndingNormalizer::getStatus() const {
    std::ostringstream oss;
    oss << "LineEndingNormalizer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void LineEndingNormalizer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::crossplatform
