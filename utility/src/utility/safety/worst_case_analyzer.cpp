#include <voltron/utility/safety/worst_case_analyzer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::safety {

WorstCaseAnalyzer& WorstCaseAnalyzer::instance() {
    static WorstCaseAnalyzer instance;
    return instance;
}

void WorstCaseAnalyzer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[WorstCaseAnalyzer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void WorstCaseAnalyzer::shutdown() {
    enabled_ = false;
    std::cout << "[WorstCaseAnalyzer] Shutdown\n";
}

bool WorstCaseAnalyzer::isEnabled() const {
    return enabled_;
}

void WorstCaseAnalyzer::enable() {
    enabled_ = true;
}

void WorstCaseAnalyzer::disable() {
    enabled_ = false;
}

std::string WorstCaseAnalyzer::getStatus() const {
    std::ostringstream oss;
    oss << "WorstCaseAnalyzer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void WorstCaseAnalyzer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::safety
