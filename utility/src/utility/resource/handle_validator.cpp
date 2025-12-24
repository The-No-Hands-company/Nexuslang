#include <voltron/utility/resource/handle_validator.h>
#include <iostream>

namespace voltron::utility::resource {

HandleValidator& HandleValidator::instance() {
    static HandleValidator instance;
    return instance;
}

void HandleValidator::initialize() {
    enabled_ = true;
    std::cout << "[HandleValidator] Initialized\n";
}

void HandleValidator::shutdown() {
    enabled_ = false;
    std::cout << "[HandleValidator] Shutdown\n";
}

bool HandleValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::resource
