#include <voltron/utility/compiler/template_instantiation_tracker.h>
#include <iostream>

namespace voltron::utility::compiler {

TemplateInstantiationTracker& TemplateInstantiationTracker::instance() {
    static TemplateInstantiationTracker instance;
    return instance;
}

void TemplateInstantiationTracker::initialize() {
    enabled_ = true;
    std::cout << "[TemplateInstantiationTracker] Initialized\n";
}

void TemplateInstantiationTracker::shutdown() {
    enabled_ = false;
    std::cout << "[TemplateInstantiationTracker] Shutdown\n";
}

bool TemplateInstantiationTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::compiler
