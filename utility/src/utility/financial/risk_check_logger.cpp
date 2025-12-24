#include <voltron/utility/financial/risk_check_logger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::financial {

RiskCheckLogger& RiskCheckLogger::instance() {
    static RiskCheckLogger instance;
    return instance;
}

void RiskCheckLogger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[RiskCheckLogger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void RiskCheckLogger::shutdown() {
    enabled_ = false;
    std::cout << "[RiskCheckLogger] Shutdown\n";
}

bool RiskCheckLogger::isEnabled() const {
    return enabled_;
}

void RiskCheckLogger::enable() {
    enabled_ = true;
}

void RiskCheckLogger::disable() {
    enabled_ = false;
}

std::string RiskCheckLogger::getStatus() const {
    std::ostringstream oss;
    oss << "RiskCheckLogger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void RiskCheckLogger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::financial
