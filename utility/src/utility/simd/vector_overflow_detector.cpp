#include <voltron/utility/simd/vector_overflow_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::simd {

VectorOverflowDetector& VectorOverflowDetector::instance() {
    static VectorOverflowDetector instance;
    return instance;
}

void VectorOverflowDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[VectorOverflowDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void VectorOverflowDetector::shutdown() {
    enabled_ = false;
    std::cout << "[VectorOverflowDetector] Shutdown\n";
}

bool VectorOverflowDetector::isEnabled() const {
    return enabled_;
}

void VectorOverflowDetector::enable() {
    enabled_ = true;
}

void VectorOverflowDetector::disable() {
    enabled_ = false;
}

std::string VectorOverflowDetector::getStatus() const {
    std::ostringstream oss;
    oss << "VectorOverflowDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void VectorOverflowDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::simd
