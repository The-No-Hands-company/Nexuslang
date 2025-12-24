#include <voltron/utility/config/dependency_injector_debug.h>
#include <iostream>

namespace voltron::utility::config {

DependencyInjectorDebug& DependencyInjectorDebug::instance() {
    static DependencyInjectorDebug instance;
    return instance;
}

void DependencyInjectorDebug::initialize() {
    enabled_ = true;
    std::cout << "[DependencyInjectorDebug] Initialized\n";
}

void DependencyInjectorDebug::shutdown() {
    enabled_ = false;
    std::cout << "[DependencyInjectorDebug] Shutdown\n";
}

bool DependencyInjectorDebug::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::config
