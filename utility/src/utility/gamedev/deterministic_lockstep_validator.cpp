#include <voltron/utility/gamedev/deterministic_lockstep_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::gamedev {

DeterministicLockstepValidator& DeterministicLockstepValidator::instance() {
    static DeterministicLockstepValidator instance;
    return instance;
}

void DeterministicLockstepValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DeterministicLockstepValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DeterministicLockstepValidator::shutdown() {
    enabled_ = false;
    std::cout << "[DeterministicLockstepValidator] Shutdown\n";
}

bool DeterministicLockstepValidator::isEnabled() const {
    return enabled_;
}

void DeterministicLockstepValidator::enable() {
    enabled_ = true;
}

void DeterministicLockstepValidator::disable() {
    enabled_ = false;
}

std::string DeterministicLockstepValidator::getStatus() const {
    std::ostringstream oss;
    oss << "DeterministicLockstepValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DeterministicLockstepValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::gamedev
