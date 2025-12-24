#include <voltron/utility/timing/timer_wheel_inspector.h>
#include <iostream>

namespace voltron::utility::timing {

TimerWheelInspector& TimerWheelInspector::instance() {
    static TimerWheelInspector instance;
    return instance;
}

void TimerWheelInspector::initialize() {
    enabled_ = true;
    std::cout << "[TimerWheelInspector] Initialized\n";
}

void TimerWheelInspector::shutdown() {
    enabled_ = false;
    std::cout << "[TimerWheelInspector] Shutdown\n";
}

bool TimerWheelInspector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::timing
