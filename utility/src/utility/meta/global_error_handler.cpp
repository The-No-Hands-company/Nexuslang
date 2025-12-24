#include <voltron/utility/meta/global_error_handler.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::meta {

GlobalErrorHandler& GlobalErrorHandler::instance() {
    static GlobalErrorHandler instance;
    return instance;
}

void GlobalErrorHandler::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[GlobalErrorHandler] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void GlobalErrorHandler::shutdown() {
    enabled_ = false;
    std::cout << "[GlobalErrorHandler] Shutdown\n";
}

bool GlobalErrorHandler::isEnabled() const {
    return enabled_;
}

void GlobalErrorHandler::enable() {
    enabled_ = true;
}

void GlobalErrorHandler::disable() {
    enabled_ = false;
}

std::string GlobalErrorHandler::getStatus() const {
    std::ostringstream oss;
    oss << "GlobalErrorHandler - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void GlobalErrorHandler::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::meta
