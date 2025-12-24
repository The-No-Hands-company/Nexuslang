#include <voltron/utility/string/zero_terminated_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::string {

ZeroTerminatedValidator& ZeroTerminatedValidator::instance() {
    static ZeroTerminatedValidator instance;
    return instance;
}

void ZeroTerminatedValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ZeroTerminatedValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ZeroTerminatedValidator::shutdown() {
    enabled_ = false;
    std::cout << "[ZeroTerminatedValidator] Shutdown\n";
}

bool ZeroTerminatedValidator::isEnabled() const {
    return enabled_;
}

void ZeroTerminatedValidator::enable() {
    enabled_ = true;
}

void ZeroTerminatedValidator::disable() {
    enabled_ = false;
}

std::string ZeroTerminatedValidator::getStatus() const {
    std::ostringstream oss;
    oss << "ZeroTerminatedValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ZeroTerminatedValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::string
