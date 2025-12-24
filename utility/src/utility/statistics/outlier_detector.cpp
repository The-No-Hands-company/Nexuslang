#include <voltron/utility/statistics/outlier_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::statistics {

OutlierDetector& OutlierDetector::instance() {
    static OutlierDetector instance;
    return instance;
}

void OutlierDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[OutlierDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void OutlierDetector::shutdown() {
    enabled_ = false;
    std::cout << "[OutlierDetector] Shutdown\n";
}

bool OutlierDetector::isEnabled() const {
    return enabled_;
}

void OutlierDetector::enable() {
    enabled_ = true;
}

void OutlierDetector::disable() {
    enabled_ = false;
}

std::string OutlierDetector::getStatus() const {
    std::ostringstream oss;
    oss << "OutlierDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void OutlierDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::statistics
