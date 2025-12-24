#include <voltron/utility/cloud/serverless_cold_start_profiler.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::cloud {

ServerlessColdStartProfiler& ServerlessColdStartProfiler::instance() {
    static ServerlessColdStartProfiler instance;
    return instance;
}

void ServerlessColdStartProfiler::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ServerlessColdStartProfiler] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ServerlessColdStartProfiler::shutdown() {
    enabled_ = false;
    std::cout << "[ServerlessColdStartProfiler] Shutdown\n";
}

bool ServerlessColdStartProfiler::isEnabled() const {
    return enabled_;
}

void ServerlessColdStartProfiler::enable() {
    enabled_ = true;
}

void ServerlessColdStartProfiler::disable() {
    enabled_ = false;
}

std::string ServerlessColdStartProfiler::getStatus() const {
    std::ostringstream oss;
    oss << "ServerlessColdStartProfiler - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ServerlessColdStartProfiler::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::cloud
