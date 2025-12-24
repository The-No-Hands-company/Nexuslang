#include <voltron/utility/ml/training_metrics_logger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::ml {

TrainingMetricsLogger& TrainingMetricsLogger::instance() {
    static TrainingMetricsLogger instance;
    return instance;
}

void TrainingMetricsLogger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[TrainingMetricsLogger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void TrainingMetricsLogger::shutdown() {
    enabled_ = false;
    std::cout << "[TrainingMetricsLogger] Shutdown\n";
}

bool TrainingMetricsLogger::isEnabled() const {
    return enabled_;
}

void TrainingMetricsLogger::enable() {
    enabled_ = true;
}

void TrainingMetricsLogger::disable() {
    enabled_ = false;
}

std::string TrainingMetricsLogger::getStatus() const {
    std::ostringstream oss;
    oss << "TrainingMetricsLogger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void TrainingMetricsLogger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::ml
