#include <voltron/utility/concurrency/race_detector_helper.h>
#include <iostream>

namespace voltron::utility::concurrency {

RaceDetectorHelper& RaceDetectorHelper::instance() {
    static RaceDetectorHelper instance;
    return instance;
}

void RaceDetectorHelper::initialize() {
    enabled_ = true;
    std::cout << "[RaceDetectorHelper] Initialized\n";
}

void RaceDetectorHelper::shutdown() {
    enabled_ = false;
    std::cout << "[RaceDetectorHelper] Shutdown\n";
}

bool RaceDetectorHelper::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::concurrency
