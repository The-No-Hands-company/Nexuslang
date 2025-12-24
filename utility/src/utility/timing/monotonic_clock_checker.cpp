#include <voltron/utility/timing/monotonic_clock_checker.h>
#include <iostream>

namespace voltron::utility::timing {

MonotonicClockChecker& MonotonicClockChecker::instance() {
    static MonotonicClockChecker instance;
    return instance;
}

void MonotonicClockChecker::initialize() {
    enabled_ = true;
    std::cout << "[MonotonicClockChecker] Initialized\n";
}

void MonotonicClockChecker::shutdown() {
    enabled_ = false;
    std::cout << "[MonotonicClockChecker] Shutdown\n";
}

bool MonotonicClockChecker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::timing
