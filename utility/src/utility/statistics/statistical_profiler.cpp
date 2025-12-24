#include <voltron/utility/statistics/statistical_profiler.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::statistics {

StatisticalProfiler& StatisticalProfiler::instance() {
    static StatisticalProfiler instance;
    return instance;
}

void StatisticalProfiler::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[StatisticalProfiler] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void StatisticalProfiler::shutdown() {
    enabled_ = false;
    std::cout << "[StatisticalProfiler] Shutdown\n";
}

bool StatisticalProfiler::isEnabled() const {
    return enabled_;
}

void StatisticalProfiler::enable() {
    enabled_ = true;
}

void StatisticalProfiler::disable() {
    enabled_ = false;
}

std::string StatisticalProfiler::getStatus() const {
    std::ostringstream oss;
    oss << "StatisticalProfiler - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void StatisticalProfiler::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::statistics
