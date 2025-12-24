#include <voltron/utility/system/dependency_checker.h>
#include <iostream>

namespace voltron::utility::system {

DependencyChecker& DependencyChecker::instance() {
    static DependencyChecker instance;
    return instance;
}

void DependencyChecker::initialize() {
    enabled_ = true;
    std::cout << "[DependencyChecker] Initialized\n";
}

void DependencyChecker::shutdown() {
    enabled_ = false;
    std::cout << "[DependencyChecker] Shutdown\n";
}

bool DependencyChecker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::system
