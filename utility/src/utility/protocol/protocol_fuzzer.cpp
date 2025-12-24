#include <voltron/utility/protocol/protocol_fuzzer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::protocol {

ProtocolFuzzer& ProtocolFuzzer::instance() {
    static ProtocolFuzzer instance;
    return instance;
}

void ProtocolFuzzer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ProtocolFuzzer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ProtocolFuzzer::shutdown() {
    enabled_ = false;
    std::cout << "[ProtocolFuzzer] Shutdown\n";
}

bool ProtocolFuzzer::isEnabled() const {
    return enabled_;
}

void ProtocolFuzzer::enable() {
    enabled_ = true;
}

void ProtocolFuzzer::disable() {
    enabled_ = false;
}

std::string ProtocolFuzzer::getStatus() const {
    std::ostringstream oss;
    oss << "ProtocolFuzzer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ProtocolFuzzer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::protocol
