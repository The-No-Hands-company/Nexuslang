#include <voltron/utility/resource/resource_leak_detector.h>
#include <iostream>

namespace voltron::utility::resource {

ResourceLeakDetector& ResourceLeakDetector::instance() {
    static ResourceLeakDetector instance;
    return instance;
}

void ResourceLeakDetector::initialize() {
    enabled_ = true;
    std::cout << "[ResourceLeakDetector] Initialized\n";
}

void ResourceLeakDetector::shutdown() {
    enabled_ = false;
    std::cout << "[ResourceLeakDetector] Shutdown\n";
}

bool ResourceLeakDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::resource
