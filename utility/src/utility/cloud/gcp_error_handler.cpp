#include <voltron/utility/cloud/gcp_error_handler.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::cloud {

GcpErrorHandler& GcpErrorHandler::instance() {
    static GcpErrorHandler instance;
    return instance;
}

void GcpErrorHandler::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[GcpErrorHandler] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void GcpErrorHandler::shutdown() {
    enabled_ = false;
    std::cout << "[GcpErrorHandler] Shutdown\n";
}

bool GcpErrorHandler::isEnabled() const {
    return enabled_;
}

void GcpErrorHandler::enable() {
    enabled_ = true;
}

void GcpErrorHandler::disable() {
    enabled_ = false;
}

std::string GcpErrorHandler::getStatus() const {
    std::ostringstream oss;
    oss << "GcpErrorHandler - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void GcpErrorHandler::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::cloud
