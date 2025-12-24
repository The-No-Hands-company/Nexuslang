#include <voltron/utility/documentation/annotation_extractor.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::documentation {

AnnotationExtractor& AnnotationExtractor::instance() {
    static AnnotationExtractor instance;
    return instance;
}

void AnnotationExtractor::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AnnotationExtractor] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AnnotationExtractor::shutdown() {
    enabled_ = false;
    std::cout << "[AnnotationExtractor] Shutdown\n";
}

bool AnnotationExtractor::isEnabled() const {
    return enabled_;
}

void AnnotationExtractor::enable() {
    enabled_ = true;
}

void AnnotationExtractor::disable() {
    enabled_ = false;
}

std::string AnnotationExtractor::getStatus() const {
    std::ostringstream oss;
    oss << "AnnotationExtractor - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AnnotationExtractor::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::documentation
