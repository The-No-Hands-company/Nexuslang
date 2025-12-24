#include <voltron/utility/protocol/handshake_tracer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::protocol {

HandshakeTracer& HandshakeTracer::instance() {
    static HandshakeTracer instance;
    return instance;
}

void HandshakeTracer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[HandshakeTracer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void HandshakeTracer::shutdown() {
    enabled_ = false;
    std::cout << "[HandshakeTracer] Shutdown\n";
}

bool HandshakeTracer::isEnabled() const {
    return enabled_;
}

void HandshakeTracer::enable() {
    enabled_ = true;
}

void HandshakeTracer::disable() {
    enabled_ = false;
}

std::string HandshakeTracer::getStatus() const {
    std::ostringstream oss;
    oss << "HandshakeTracer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void HandshakeTracer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::protocol
