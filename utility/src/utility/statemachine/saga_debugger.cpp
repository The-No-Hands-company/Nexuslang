#include <voltron/utility/statemachine/saga_debugger.h>
#include <iostream>

namespace voltron::utility::statemachine {

SagaDebugger& SagaDebugger::instance() {
    static SagaDebugger instance;
    return instance;
}

void SagaDebugger::initialize() {
    enabled_ = true;
    std::cout << "[SagaDebugger] Initialized\n";
}

void SagaDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[SagaDebugger] Shutdown\n";
}

bool SagaDebugger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::statemachine
