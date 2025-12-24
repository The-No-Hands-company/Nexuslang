#include <voltron/utility/formal/invariant_prover_helper.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::formal {

InvariantProverHelper& InvariantProverHelper::instance() {
    static InvariantProverHelper instance;
    return instance;
}

void InvariantProverHelper::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[InvariantProverHelper] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void InvariantProverHelper::shutdown() {
    enabled_ = false;
    std::cout << "[InvariantProverHelper] Shutdown\n";
}

bool InvariantProverHelper::isEnabled() const {
    return enabled_;
}

void InvariantProverHelper::enable() {
    enabled_ = true;
}

void InvariantProverHelper::disable() {
    enabled_ = false;
}

std::string InvariantProverHelper::getStatus() const {
    std::ostringstream oss;
    oss << "InvariantProverHelper - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void InvariantProverHelper::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::formal
