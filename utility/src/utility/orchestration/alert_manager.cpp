#include <voltron/utility/orchestration/alert_manager.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::orchestration {

AlertManager& AlertManager::instance() {
    static AlertManager instance;
    return instance;
}

void AlertManager::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AlertManager] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AlertManager::shutdown() {
    enabled_ = false;
    std::cout << "[AlertManager] Shutdown\n";
}

bool AlertManager::isEnabled() const {
    return enabled_;
}

void AlertManager::enable() {
    enabled_ = true;
}

void AlertManager::disable() {
    enabled_ = false;
}

std::string AlertManager::getStatus() const {
    std::ostringstream oss;
    oss << "AlertManager - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AlertManager::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::orchestration
