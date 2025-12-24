#include <voltron/utility/reflection/property_inspector.h>
#include <iostream>

namespace voltron::utility::reflection {

PropertyInspector& PropertyInspector::instance() {
    static PropertyInspector instance;
    return instance;
}

void PropertyInspector::initialize() {
    enabled_ = true;
    std::cout << "[PropertyInspector] Initialized\n";
}

void PropertyInspector::shutdown() {
    enabled_ = false;
    std::cout << "[PropertyInspector] Shutdown\n";
}

bool PropertyInspector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::reflection
