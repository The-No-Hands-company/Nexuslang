#include <voltron/utility/graphics/framebuffer_validator.h>
#include <iostream>

namespace voltron::utility::graphics {

FramebufferValidator& FramebufferValidator::instance() {
    static FramebufferValidator instance;
    return instance;
}

void FramebufferValidator::initialize() {
    enabled_ = true;
    std::cout << "[FramebufferValidator] Initialized\n";
}

void FramebufferValidator::shutdown() {
    enabled_ = false;
    std::cout << "[FramebufferValidator] Shutdown\n";
}

bool FramebufferValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::graphics
