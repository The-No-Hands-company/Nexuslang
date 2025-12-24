#include <voltron/utility/cpp23/module_dependency_tracker.h>
#include <iostream>

namespace voltron::utility::cpp23 {

ModuleDependencyTracker& ModuleDependencyTracker::instance() {
    static ModuleDependencyTracker instance;
    return instance;
}

void ModuleDependencyTracker::initialize() {
    enabled_ = true;
    std::cout << "[ModuleDependencyTracker] Initialized\n";
}

void ModuleDependencyTracker::shutdown() {
    enabled_ = false;
    std::cout << "[ModuleDependencyTracker] Shutdown\n";
}

bool ModuleDependencyTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::cpp23
