#include <voltron/utility/allocator/fragmentation_analyzer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::allocator {

FragmentationAnalyzer& FragmentationAnalyzer::instance() {
    static FragmentationAnalyzer instance;
    return instance;
}

void FragmentationAnalyzer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[FragmentationAnalyzer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void FragmentationAnalyzer::shutdown() {
    enabled_ = false;
    std::cout << "[FragmentationAnalyzer] Shutdown\n";
}

bool FragmentationAnalyzer::isEnabled() const {
    return enabled_;
}

void FragmentationAnalyzer::enable() {
    enabled_ = true;
}

void FragmentationAnalyzer::disable() {
    enabled_ = false;
}

std::string FragmentationAnalyzer::getStatus() const {
    std::ostringstream oss;
    oss << "FragmentationAnalyzer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void FragmentationAnalyzer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::allocator
