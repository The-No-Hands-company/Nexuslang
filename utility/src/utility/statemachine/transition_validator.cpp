#include <voltron/utility/statemachine/transition_validator.h>
#include <iostream>

namespace voltron::utility::statemachine {

TransitionValidator& TransitionValidator::instance() {
    static TransitionValidator instance;
    return instance;
}

void TransitionValidator::initialize() {
    enabled_ = true;
    std::cout << "[TransitionValidator] Initialized\n";
}

void TransitionValidator::shutdown() {
    enabled_ = false;
    std::cout << "[TransitionValidator] Shutdown\n";
}

bool TransitionValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::statemachine
