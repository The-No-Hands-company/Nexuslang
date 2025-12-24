#include <voltron/utility/cloud/cloud_quota_monitor.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::cloud {

CloudQuotaMonitor& CloudQuotaMonitor::instance() {
    static CloudQuotaMonitor instance;
    return instance;
}

void CloudQuotaMonitor::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CloudQuotaMonitor] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CloudQuotaMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[CloudQuotaMonitor] Shutdown\n";
}

bool CloudQuotaMonitor::isEnabled() const {
    return enabled_;
}

void CloudQuotaMonitor::enable() {
    enabled_ = true;
}

void CloudQuotaMonitor::disable() {
    enabled_ = false;
}

std::string CloudQuotaMonitor::getStatus() const {
    std::ostringstream oss;
    oss << "CloudQuotaMonitor - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CloudQuotaMonitor::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::cloud
