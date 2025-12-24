#include <voltron/utility/network/network_partition_simulator.h>
#include <iostream>

namespace voltron::utility::network {

NetworkPartitionSimulator& NetworkPartitionSimulator::instance() {
    static NetworkPartitionSimulator instance;
    return instance;
}

void NetworkPartitionSimulator::initialize() {
    enabled_ = true;
    std::cout << "[NetworkPartitionSimulator] Initialized\n";
}

void NetworkPartitionSimulator::shutdown() {
    enabled_ = false;
    std::cout << "[NetworkPartitionSimulator] Shutdown\n";
}

bool NetworkPartitionSimulator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::network
