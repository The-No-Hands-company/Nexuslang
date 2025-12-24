#include <voltron/utility/plugin/dlopen_wrapper.h>
#include <iostream>

namespace voltron::utility::plugin {

DlopenWrapper& DlopenWrapper::instance() {
    static DlopenWrapper instance;
    return instance;
}

void DlopenWrapper::initialize() {
    enabled_ = true;
}

void DlopenWrapper::shutdown() {
    enabled_ = false;
}

bool DlopenWrapper::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::plugin
