#include <voltron/utility/meta/report_aggregator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::meta {

ReportAggregator& ReportAggregator::instance() {
    static ReportAggregator instance;
    return instance;
}

void ReportAggregator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ReportAggregator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ReportAggregator::shutdown() {
    enabled_ = false;
    std::cout << "[ReportAggregator] Shutdown\n";
}

bool ReportAggregator::isEnabled() const {
    return enabled_;
}

void ReportAggregator::enable() {
    enabled_ = true;
}

void ReportAggregator::disable() {
    enabled_ = false;
}

std::string ReportAggregator::getStatus() const {
    std::ostringstream oss;
    oss << "ReportAggregator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ReportAggregator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::meta
