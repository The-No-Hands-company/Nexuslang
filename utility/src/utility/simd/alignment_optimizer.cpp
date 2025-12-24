#include <voltron/utility/simd/alignment_optimizer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::simd {

AlignmentOptimizer& AlignmentOptimizer::instance() {
    static AlignmentOptimizer instance;
    return instance;
}

void AlignmentOptimizer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AlignmentOptimizer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AlignmentOptimizer::shutdown() {
    enabled_ = false;
    std::cout << "[AlignmentOptimizer] Shutdown\n";
}

bool AlignmentOptimizer::isEnabled() const {
    return enabled_;
}

void AlignmentOptimizer::enable() {
    enabled_ = true;
}

void AlignmentOptimizer::disable() {
    enabled_ = false;
}

std::string AlignmentOptimizer::getStatus() const {
    std::ostringstream oss;
    oss << "AlignmentOptimizer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AlignmentOptimizer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::simd
