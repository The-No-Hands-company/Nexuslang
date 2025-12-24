#include <voltron/utility/config/environment_diff_detector.h>
#include <iostream>

namespace voltron::utility::config {

EnvironmentDiffDetector& EnvironmentDiffDetector::instance() {
    static EnvironmentDiffDetector instance;
    return instance;
}

void EnvironmentDiffDetector::initialize() {
    enabled_ = true;
    std::cout << "[EnvironmentDiffDetector] Initialized\n";
}

void EnvironmentDiffDetector::shutdown() {
    enabled_ = false;
    std::cout << "[EnvironmentDiffDetector] Shutdown\n";
}

bool EnvironmentDiffDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::config
