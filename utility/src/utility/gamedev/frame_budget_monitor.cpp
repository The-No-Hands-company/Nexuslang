#include <voltron/utility/gamedev/frame_budget_monitor.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::gamedev {

FrameBudgetMonitor& FrameBudgetMonitor::instance() {
    static FrameBudgetMonitor instance;
    return instance;
}

void FrameBudgetMonitor::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[FrameBudgetMonitor] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void FrameBudgetMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[FrameBudgetMonitor] Shutdown\n";
}

bool FrameBudgetMonitor::isEnabled() const {
    return enabled_;
}

void FrameBudgetMonitor::enable() {
    enabled_ = true;
}

void FrameBudgetMonitor::disable() {
    enabled_ = false;
}

std::string FrameBudgetMonitor::getStatus() const {
    std::ostringstream oss;
    oss << "FrameBudgetMonitor - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void FrameBudgetMonitor::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::gamedev
