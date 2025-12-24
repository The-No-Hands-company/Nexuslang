#include <voltron/utility/chaos/cpu_throttler.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::chaos {

CpuThrottler& CpuThrottler::instance() {
    static CpuThrottler instance;
    return instance;
}

void CpuThrottler::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CpuThrottler] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CpuThrottler::shutdown() {
    enabled_ = false;
    std::cout << "[CpuThrottler] Shutdown\n";
}

bool CpuThrottler::isEnabled() const {
    return enabled_;
}

void CpuThrottler::enable() {
    enabled_ = true;
}

void CpuThrottler::disable() {
    enabled_ = false;
}

std::string CpuThrottler::getStatus() const {
    std::ostringstream oss;
    oss << "CpuThrottler - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CpuThrottler::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::chaos
