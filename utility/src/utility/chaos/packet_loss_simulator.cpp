#include <voltron/utility/chaos/packet_loss_simulator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::chaos {

PacketLossSimulator& PacketLossSimulator::instance() {
    static PacketLossSimulator instance;
    return instance;
}

void PacketLossSimulator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PacketLossSimulator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PacketLossSimulator::shutdown() {
    enabled_ = false;
    std::cout << "[PacketLossSimulator] Shutdown\n";
}

bool PacketLossSimulator::isEnabled() const {
    return enabled_;
}

void PacketLossSimulator::enable() {
    enabled_ = true;
}

void PacketLossSimulator::disable() {
    enabled_ = false;
}

std::string PacketLossSimulator::getStatus() const {
    std::ostringstream oss;
    oss << "PacketLossSimulator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PacketLossSimulator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::chaos
