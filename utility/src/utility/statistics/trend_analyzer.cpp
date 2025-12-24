#include <voltron/utility/statistics/trend_analyzer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::statistics {

TrendAnalyzer& TrendAnalyzer::instance() {
    static TrendAnalyzer instance;
    return instance;
}

void TrendAnalyzer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[TrendAnalyzer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void TrendAnalyzer::shutdown() {
    enabled_ = false;
    std::cout << "[TrendAnalyzer] Shutdown\n";
}

bool TrendAnalyzer::isEnabled() const {
    return enabled_;
}

void TrendAnalyzer::enable() {
    enabled_ = true;
}

void TrendAnalyzer::disable() {
    enabled_ = false;
}

std::string TrendAnalyzer::getStatus() const {
    std::ostringstream oss;
    oss << "TrendAnalyzer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void TrendAnalyzer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::statistics
