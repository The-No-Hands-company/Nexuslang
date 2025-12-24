#include <voltron/utility/cpp23/coroutine_leak_detector.h>
#include <iostream>

namespace voltron::utility::cpp23 {

CoroutineLeakDetector& CoroutineLeakDetector::instance() {
    static CoroutineLeakDetector instance;
    return instance;
}

void CoroutineLeakDetector::initialize() {
    enabled_ = true;
    std::cout << "[CoroutineLeakDetector] Initialized\n";
}

void CoroutineLeakDetector::shutdown() {
    enabled_ = false;
    std::cout << "[CoroutineLeakDetector] Shutdown\n";
}

bool CoroutineLeakDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::cpp23
