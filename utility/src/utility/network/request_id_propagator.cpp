#include <voltron/utility/network/request_id_propagator.h>
#include <iostream>

namespace voltron::utility::network {

RequestIdPropagator& RequestIdPropagator::instance() {
    static RequestIdPropagator instance;
    return instance;
}

void RequestIdPropagator::initialize() {
    enabled_ = true;
    std::cout << "[RequestIdPropagator] Initialized\n";
}

void RequestIdPropagator::shutdown() {
    enabled_ = false;
    std::cout << "[RequestIdPropagator] Shutdown\n";
}

bool RequestIdPropagator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::network
