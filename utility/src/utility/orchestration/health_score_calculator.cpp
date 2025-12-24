#include <voltron/utility/orchestration/health_score_calculator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::orchestration {

HealthScoreCalculator& HealthScoreCalculator::instance() {
    static HealthScoreCalculator instance;
    return instance;
}

void HealthScoreCalculator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[HealthScoreCalculator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void HealthScoreCalculator::shutdown() {
    enabled_ = false;
    std::cout << "[HealthScoreCalculator] Shutdown\n";
}

bool HealthScoreCalculator::isEnabled() const {
    return enabled_;
}

void HealthScoreCalculator::enable() {
    enabled_ = true;
}

void HealthScoreCalculator::disable() {
    enabled_ = false;
}

std::string HealthScoreCalculator::getStatus() const {
    std::ostringstream oss;
    oss << "HealthScoreCalculator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void HealthScoreCalculator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::orchestration
