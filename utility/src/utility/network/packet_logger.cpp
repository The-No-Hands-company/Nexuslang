#include <voltron/utility/network/packet_logger.h>
#include <iostream>

namespace voltron::utility::network {

PacketLogger& PacketLogger::instance() {
    static PacketLogger instance;
    return instance;
}

void PacketLogger::initialize() {
    enabled_ = true;
    std::cout << "[PacketLogger] Initialized\n";
}

void PacketLogger::shutdown() {
    enabled_ = false;
    std::cout << "[PacketLogger] Shutdown\n";
}

bool PacketLogger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::network
