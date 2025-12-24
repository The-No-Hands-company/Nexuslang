#include <voltron/utility/cloud/spot_instance_handler.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::cloud {

SpotInstanceHandler& SpotInstanceHandler::instance() {
    static SpotInstanceHandler instance;
    return instance;
}

void SpotInstanceHandler::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[SpotInstanceHandler] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void SpotInstanceHandler::shutdown() {
    enabled_ = false;
    std::cout << "[SpotInstanceHandler] Shutdown\n";
}

bool SpotInstanceHandler::isEnabled() const {
    return enabled_;
}

void SpotInstanceHandler::enable() {
    enabled_ = true;
}

void SpotInstanceHandler::disable() {
    enabled_ = false;
}

std::string SpotInstanceHandler::getStatus() const {
    std::ostringstream oss;
    oss << "SpotInstanceHandler - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void SpotInstanceHandler::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::cloud
