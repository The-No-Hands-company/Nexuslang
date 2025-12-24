#include <voltron/utility/allocator/allocation_pattern_analyzer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::allocator {

AllocationPatternAnalyzer& AllocationPatternAnalyzer::instance() {
    static AllocationPatternAnalyzer instance;
    return instance;
}

void AllocationPatternAnalyzer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AllocationPatternAnalyzer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AllocationPatternAnalyzer::shutdown() {
    enabled_ = false;
    std::cout << "[AllocationPatternAnalyzer] Shutdown\n";
}

bool AllocationPatternAnalyzer::isEnabled() const {
    return enabled_;
}

void AllocationPatternAnalyzer::enable() {
    enabled_ = true;
}

void AllocationPatternAnalyzer::disable() {
    enabled_ = false;
}

std::string AllocationPatternAnalyzer::getStatus() const {
    std::ostringstream oss;
    oss << "AllocationPatternAnalyzer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AllocationPatternAnalyzer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::allocator
