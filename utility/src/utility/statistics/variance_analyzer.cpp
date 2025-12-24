#include <voltron/utility/statistics/variance_analyzer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::statistics {

VarianceAnalyzer& VarianceAnalyzer::instance() {
    static VarianceAnalyzer instance;
    return instance;
}

void VarianceAnalyzer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[VarianceAnalyzer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void VarianceAnalyzer::shutdown() {
    enabled_ = false;
    std::cout << "[VarianceAnalyzer] Shutdown\n";
}

bool VarianceAnalyzer::isEnabled() const {
    return enabled_;
}

void VarianceAnalyzer::enable() {
    enabled_ = true;
}

void VarianceAnalyzer::disable() {
    enabled_ = false;
}

std::string VarianceAnalyzer::getStatus() const {
    std::ostringstream oss;
    oss << "VarianceAnalyzer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void VarianceAnalyzer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::statistics
