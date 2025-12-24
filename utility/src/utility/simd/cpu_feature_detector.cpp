#include <voltron/utility/simd/cpu_feature_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::simd {

CpuFeatureDetector& CpuFeatureDetector::instance() {
    static CpuFeatureDetector instance;
    return instance;
}

void CpuFeatureDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CpuFeatureDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CpuFeatureDetector::shutdown() {
    enabled_ = false;
    std::cout << "[CpuFeatureDetector] Shutdown\n";
}

bool CpuFeatureDetector::isEnabled() const {
    return enabled_;
}

void CpuFeatureDetector::enable() {
    enabled_ = true;
}

void CpuFeatureDetector::disable() {
    enabled_ = false;
}

std::string CpuFeatureDetector::getStatus() const {
    std::ostringstream oss;
    oss << "CpuFeatureDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CpuFeatureDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::simd
