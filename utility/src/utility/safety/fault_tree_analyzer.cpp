#include <voltron/utility/safety/fault_tree_analyzer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::safety {

FaultTreeAnalyzer& FaultTreeAnalyzer::instance() {
    static FaultTreeAnalyzer instance;
    return instance;
}

void FaultTreeAnalyzer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[FaultTreeAnalyzer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void FaultTreeAnalyzer::shutdown() {
    enabled_ = false;
    std::cout << "[FaultTreeAnalyzer] Shutdown\n";
}

bool FaultTreeAnalyzer::isEnabled() const {
    return enabled_;
}

void FaultTreeAnalyzer::enable() {
    enabled_ = true;
}

void FaultTreeAnalyzer::disable() {
    enabled_ = false;
}

std::string FaultTreeAnalyzer::getStatus() const {
    std::ostringstream oss;
    oss << "FaultTreeAnalyzer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void FaultTreeAnalyzer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::safety
