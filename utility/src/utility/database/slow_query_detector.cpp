#include <voltron/utility/database/slow_query_detector.h>
#include <iostream>

namespace voltron::utility::database {

SlowQueryDetector& SlowQueryDetector::instance() {
    static SlowQueryDetector instance;
    return instance;
}

void SlowQueryDetector::initialize() {
    enabled_ = true;
    std::cout << "[SlowQueryDetector] Initialized\n";
}

void SlowQueryDetector::shutdown() {
    enabled_ = false;
    std::cout << "[SlowQueryDetector] Shutdown\n";
}

bool SlowQueryDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::database
