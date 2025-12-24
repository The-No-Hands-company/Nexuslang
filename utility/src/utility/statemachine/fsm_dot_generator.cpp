#include <voltron/utility/statemachine/fsm_dot_generator.h>
#include <iostream>

namespace voltron::utility::statemachine {

FsmDotGenerator& FsmDotGenerator::instance() {
    static FsmDotGenerator instance;
    return instance;
}

void FsmDotGenerator::initialize() {
    enabled_ = true;
    std::cout << "[FsmDotGenerator] Initialized\n";
}

void FsmDotGenerator::shutdown() {
    enabled_ = false;
    std::cout << "[FsmDotGenerator] Shutdown\n";
}

bool FsmDotGenerator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::statemachine
