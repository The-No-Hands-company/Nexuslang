#include <voltron/utility/datastructures/hash_collision_detector.h>
#include <iostream>

namespace voltron::utility::datastructures {

HashCollisionDetector& HashCollisionDetector::instance() {
    static HashCollisionDetector instance;
    return instance;
}

void HashCollisionDetector::initialize() {
    enabled_ = true;
    std::cout << "[HashCollisionDetector] Initialized\n";
}

void HashCollisionDetector::shutdown() {
    enabled_ = false;
    std::cout << "[HashCollisionDetector] Shutdown\n";
}

bool HashCollisionDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::datastructures
