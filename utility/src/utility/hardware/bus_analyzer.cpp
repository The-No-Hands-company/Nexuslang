#include <voltron/utility/hardware/bus_analyzer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::hardware {

BusAnalyzer& BusAnalyzer::instance() {
    static BusAnalyzer instance;
    return instance;
}

void BusAnalyzer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[BusAnalyzer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void BusAnalyzer::shutdown() {
    enabled_ = false;
    std::cout << "[BusAnalyzer] Shutdown\n";
}

bool BusAnalyzer::isEnabled() const {
    return enabled_;
}

void BusAnalyzer::enable() {
    enabled_ = true;
}

void BusAnalyzer::disable() {
    enabled_ = false;
}

std::string BusAnalyzer::getStatus() const {
    std::ostringstream oss;
    oss << "BusAnalyzer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void BusAnalyzer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::hardware
