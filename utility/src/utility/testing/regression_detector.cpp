#include <voltron/utility/testing/regression_detector.h>
#include <iostream>

namespace voltron::utility::testing {

RegressionDetector& RegressionDetector::instance() {
    static RegressionDetector instance;
    return instance;
}

void RegressionDetector::initialize() {
    enabled_ = true;
    std::cout << "[RegressionDetector] Initialized\n";
}

void RegressionDetector::shutdown() {
    enabled_ = false;
    std::cout << "[RegressionDetector] Shutdown\n";
}

bool RegressionDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::testing
