#include <voltron/utility/hardware/battery_diagnostics.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::hardware {

BatteryDiagnostics& BatteryDiagnostics::instance() {
    static BatteryDiagnostics instance;
    return instance;
}

void BatteryDiagnostics::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[BatteryDiagnostics] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void BatteryDiagnostics::shutdown() {
    enabled_ = false;
    std::cout << "[BatteryDiagnostics] Shutdown\n";
}

bool BatteryDiagnostics::isEnabled() const {
    return enabled_;
}

void BatteryDiagnostics::enable() {
    enabled_ = true;
}

void BatteryDiagnostics::disable() {
    enabled_ = false;
}

std::string BatteryDiagnostics::getStatus() const {
    std::ostringstream oss;
    oss << "BatteryDiagnostics - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void BatteryDiagnostics::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::hardware
