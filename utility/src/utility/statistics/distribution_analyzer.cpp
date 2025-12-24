#include <voltron/utility/statistics/distribution_analyzer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::statistics {

DistributionAnalyzer& DistributionAnalyzer::instance() {
    static DistributionAnalyzer instance;
    return instance;
}

void DistributionAnalyzer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DistributionAnalyzer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DistributionAnalyzer::shutdown() {
    enabled_ = false;
    std::cout << "[DistributionAnalyzer] Shutdown\n";
}

bool DistributionAnalyzer::isEnabled() const {
    return enabled_;
}

void DistributionAnalyzer::enable() {
    enabled_ = true;
}

void DistributionAnalyzer::disable() {
    enabled_ = false;
}

std::string DistributionAnalyzer::getStatus() const {
    std::ostringstream oss;
    oss << "DistributionAnalyzer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DistributionAnalyzer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::statistics
