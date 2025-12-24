#include <voltron/utility/protocol/packet_capture_logger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::protocol {

PacketCaptureLogger& PacketCaptureLogger::instance() {
    static PacketCaptureLogger instance;
    return instance;
}

void PacketCaptureLogger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PacketCaptureLogger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PacketCaptureLogger::shutdown() {
    enabled_ = false;
    std::cout << "[PacketCaptureLogger] Shutdown\n";
}

bool PacketCaptureLogger::isEnabled() const {
    return enabled_;
}

void PacketCaptureLogger::enable() {
    enabled_ = true;
}

void PacketCaptureLogger::disable() {
    enabled_ = false;
}

std::string PacketCaptureLogger::getStatus() const {
    std::ostringstream oss;
    oss << "PacketCaptureLogger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PacketCaptureLogger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::protocol
