#include <voltron/utility/metrics/counter.h>
#include <iostream>

namespace voltron::utility::metrics {

Counter& Counter::instance() {
    static Counter instance;
    return instance;
}

void Counter::initialize() {
    enabled_ = true;
    std::cout << "[Counter] Initialized\n";
}

void Counter::shutdown() {
    enabled_ = false;
    std::cout << "[Counter] Shutdown\n";
}

bool Counter::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::metrics
