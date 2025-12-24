#include <voltron/utility/formal/precondition_generator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::formal {

PreconditionGenerator& PreconditionGenerator::instance() {
    static PreconditionGenerator instance;
    return instance;
}

void PreconditionGenerator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PreconditionGenerator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PreconditionGenerator::shutdown() {
    enabled_ = false;
    std::cout << "[PreconditionGenerator] Shutdown\n";
}

bool PreconditionGenerator::isEnabled() const {
    return enabled_;
}

void PreconditionGenerator::enable() {
    enabled_ = true;
}

void PreconditionGenerator::disable() {
    enabled_ = false;
}

std::string PreconditionGenerator::getStatus() const {
    std::ostringstream oss;
    oss << "PreconditionGenerator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PreconditionGenerator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::formal
