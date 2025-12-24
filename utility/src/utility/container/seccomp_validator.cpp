#include <voltron/utility/container/seccomp_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::container {

SeccompValidator& SeccompValidator::instance() {
    static SeccompValidator instance;
    return instance;
}

void SeccompValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[SeccompValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void SeccompValidator::shutdown() {
    enabled_ = false;
    std::cout << "[SeccompValidator] Shutdown\n";
}

bool SeccompValidator::isEnabled() const {
    return enabled_;
}

void SeccompValidator::enable() {
    enabled_ = true;
}

void SeccompValidator::disable() {
    enabled_ = false;
}

std::string SeccompValidator::getStatus() const {
    std::ostringstream oss;
    oss << "SeccompValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void SeccompValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::container
