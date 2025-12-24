#include <voltron/utility/hardware/pcie_error_handler.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::hardware {

PcieErrorHandler& PcieErrorHandler::instance() {
    static PcieErrorHandler instance;
    return instance;
}

void PcieErrorHandler::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PcieErrorHandler] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PcieErrorHandler::shutdown() {
    enabled_ = false;
    std::cout << "[PcieErrorHandler] Shutdown\n";
}

bool PcieErrorHandler::isEnabled() const {
    return enabled_;
}

void PcieErrorHandler::enable() {
    enabled_ = true;
}

void PcieErrorHandler::disable() {
    enabled_ = false;
}

std::string PcieErrorHandler::getStatus() const {
    std::ostringstream oss;
    oss << "PcieErrorHandler - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PcieErrorHandler::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::hardware
