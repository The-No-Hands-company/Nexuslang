#include <voltron/utility/crossplatform/system_call_wrapper.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::crossplatform {

SystemCallWrapper& SystemCallWrapper::instance() {
    static SystemCallWrapper instance;
    return instance;
}

void SystemCallWrapper::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[SystemCallWrapper] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void SystemCallWrapper::shutdown() {
    enabled_ = false;
    std::cout << "[SystemCallWrapper] Shutdown\n";
}

bool SystemCallWrapper::isEnabled() const {
    return enabled_;
}

void SystemCallWrapper::enable() {
    enabled_ = true;
}

void SystemCallWrapper::disable() {
    enabled_ = false;
}

std::string SystemCallWrapper::getStatus() const {
    std::ostringstream oss;
    oss << "SystemCallWrapper - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void SystemCallWrapper::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::crossplatform
