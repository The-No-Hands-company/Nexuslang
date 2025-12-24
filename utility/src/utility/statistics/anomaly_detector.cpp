#include <voltron/utility/statistics/anomaly_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::statistics {

AnomalyDetector& AnomalyDetector::instance() {
    static AnomalyDetector instance;
    return instance;
}

void AnomalyDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AnomalyDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AnomalyDetector::shutdown() {
    enabled_ = false;
    std::cout << "[AnomalyDetector] Shutdown\n";
}

bool AnomalyDetector::isEnabled() const {
    return enabled_;
}

void AnomalyDetector::enable() {
    enabled_ = true;
}

void AnomalyDetector::disable() {
    enabled_ = false;
}

std::string AnomalyDetector::getStatus() const {
    std::ostringstream oss;
    oss << "AnomalyDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AnomalyDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::statistics
