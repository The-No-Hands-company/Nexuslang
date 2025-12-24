#include <voltron/utility/documentation/performance_characteristics_doc.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::documentation {

PerformanceCharacteristicsDoc& PerformanceCharacteristicsDoc::instance() {
    static PerformanceCharacteristicsDoc instance;
    return instance;
}

void PerformanceCharacteristicsDoc::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PerformanceCharacteristicsDoc] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PerformanceCharacteristicsDoc::shutdown() {
    enabled_ = false;
    std::cout << "[PerformanceCharacteristicsDoc] Shutdown\n";
}

bool PerformanceCharacteristicsDoc::isEnabled() const {
    return enabled_;
}

void PerformanceCharacteristicsDoc::enable() {
    enabled_ = true;
}

void PerformanceCharacteristicsDoc::disable() {
    enabled_ = false;
}

std::string PerformanceCharacteristicsDoc::getStatus() const {
    std::ostringstream oss;
    oss << "PerformanceCharacteristicsDoc - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PerformanceCharacteristicsDoc::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::documentation
