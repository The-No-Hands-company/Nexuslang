#include <voltron/utility/protocol/packet_fragmenter_debugger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::protocol {

PacketFragmenterDebugger& PacketFragmenterDebugger::instance() {
    static PacketFragmenterDebugger instance;
    return instance;
}

void PacketFragmenterDebugger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PacketFragmenterDebugger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PacketFragmenterDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[PacketFragmenterDebugger] Shutdown\n";
}

bool PacketFragmenterDebugger::isEnabled() const {
    return enabled_;
}

void PacketFragmenterDebugger::enable() {
    enabled_ = true;
}

void PacketFragmenterDebugger::disable() {
    enabled_ = false;
}

std::string PacketFragmenterDebugger::getStatus() const {
    std::ostringstream oss;
    oss << "PacketFragmenterDebugger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PacketFragmenterDebugger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::protocol
