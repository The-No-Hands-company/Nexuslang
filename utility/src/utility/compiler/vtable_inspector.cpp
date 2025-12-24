#include <voltron/utility/compiler/vtable_inspector.h>
#include <iostream>

namespace voltron::utility::compiler {

VtableInspector& VtableInspector::instance() {
    static VtableInspector instance;
    return instance;
}

void VtableInspector::initialize() {
    enabled_ = true;
    std::cout << "[VtableInspector] Initialized\n";
}

void VtableInspector::shutdown() {
    enabled_ = false;
    std::cout << "[VtableInspector] Shutdown\n";
}

bool VtableInspector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::compiler
