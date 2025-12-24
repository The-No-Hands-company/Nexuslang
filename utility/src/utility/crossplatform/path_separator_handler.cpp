#include <voltron/utility/crossplatform/path_separator_handler.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::crossplatform {

PathSeparatorHandler& PathSeparatorHandler::instance() {
    static PathSeparatorHandler instance;
    return instance;
}

void PathSeparatorHandler::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PathSeparatorHandler] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PathSeparatorHandler::shutdown() {
    enabled_ = false;
    std::cout << "[PathSeparatorHandler] Shutdown\n";
}

bool PathSeparatorHandler::isEnabled() const {
    return enabled_;
}

void PathSeparatorHandler::enable() {
    enabled_ = true;
}

void PathSeparatorHandler::disable() {
    enabled_ = false;
}

std::string PathSeparatorHandler::getStatus() const {
    std::ostringstream oss;
    oss << "PathSeparatorHandler - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PathSeparatorHandler::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::crossplatform
