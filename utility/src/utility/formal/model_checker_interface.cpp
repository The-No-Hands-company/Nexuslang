#include <voltron/utility/formal/model_checker_interface.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::formal {

ModelCheckerInterface& ModelCheckerInterface::instance() {
    static ModelCheckerInterface instance;
    return instance;
}

void ModelCheckerInterface::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ModelCheckerInterface] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ModelCheckerInterface::shutdown() {
    enabled_ = false;
    std::cout << "[ModelCheckerInterface] Shutdown\n";
}

bool ModelCheckerInterface::isEnabled() const {
    return enabled_;
}

void ModelCheckerInterface::enable() {
    enabled_ = true;
}

void ModelCheckerInterface::disable() {
    enabled_ = false;
}

std::string ModelCheckerInterface::getStatus() const {
    std::ostringstream oss;
    oss << "ModelCheckerInterface - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ModelCheckerInterface::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::formal
