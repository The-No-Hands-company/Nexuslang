#include <voltron/utility/security/timing_attack_detector.h>
#include <iostream>

namespace voltron::utility::security {

TimingAttackDetector& TimingAttackDetector::instance() {
    static TimingAttackDetector instance;
    return instance;
}

void TimingAttackDetector::initialize() {
    enabled_ = true;
    std::cout << "[TimingAttackDetector] Initialized\n";
}

void TimingAttackDetector::shutdown() {
    enabled_ = false;
    std::cout << "[TimingAttackDetector] Shutdown\n";
}

bool TimingAttackDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::security
