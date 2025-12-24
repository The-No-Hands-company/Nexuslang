#include <voltron/utility/algorithmic/convergence_monitor.h>
#include <iostream>

namespace voltron::utility::algorithmic {

ConvergenceMonitor& ConvergenceMonitor::instance() {
    static ConvergenceMonitor instance;
    return instance;
}

void ConvergenceMonitor::initialize() {
    enabled_ = true;
}

void ConvergenceMonitor::shutdown() {
    enabled_ = false;
}

bool ConvergenceMonitor::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::algorithmic
