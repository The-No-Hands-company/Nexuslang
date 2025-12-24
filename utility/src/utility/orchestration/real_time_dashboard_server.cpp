#include <voltron/utility/orchestration/real_time_dashboard_server.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::orchestration {

RealTimeDashboardServer& RealTimeDashboardServer::instance() {
    static RealTimeDashboardServer instance;
    return instance;
}

void RealTimeDashboardServer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[RealTimeDashboardServer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void RealTimeDashboardServer::shutdown() {
    enabled_ = false;
    std::cout << "[RealTimeDashboardServer] Shutdown\n";
}

bool RealTimeDashboardServer::isEnabled() const {
    return enabled_;
}

void RealTimeDashboardServer::enable() {
    enabled_ = true;
}

void RealTimeDashboardServer::disable() {
    enabled_ = false;
}

std::string RealTimeDashboardServer::getStatus() const {
    std::ostringstream oss;
    oss << "RealTimeDashboardServer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void RealTimeDashboardServer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::orchestration
