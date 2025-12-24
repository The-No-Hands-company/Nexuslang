#include <voltron/utility/protocol/protocol_state_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::protocol {

ProtocolStateValidator& ProtocolStateValidator::instance() {
    static ProtocolStateValidator instance;
    return instance;
}

void ProtocolStateValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ProtocolStateValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ProtocolStateValidator::shutdown() {
    enabled_ = false;
    std::cout << "[ProtocolStateValidator] Shutdown\n";
}

bool ProtocolStateValidator::isEnabled() const {
    return enabled_;
}

void ProtocolStateValidator::enable() {
    enabled_ = true;
}

void ProtocolStateValidator::disable() {
    enabled_ = false;
}

std::string ProtocolStateValidator::getStatus() const {
    std::ostringstream oss;
    oss << "ProtocolStateValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ProtocolStateValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::protocol
