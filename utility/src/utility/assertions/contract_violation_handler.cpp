#include <voltron/utility/assertions/contract_violation_handler.h>
#include <iostream>

namespace voltron::utility::assertions {

ContractViolationHandler& ContractViolationHandler::instance() {
    static ContractViolationHandler instance;
    return instance;
}

void ContractViolationHandler::initialize() {
    enabled_ = true;
    std::cout << "[ContractViolationHandler] Initialized\n";
}

void ContractViolationHandler::shutdown() {
    enabled_ = false;
    std::cout << "[ContractViolationHandler] Shutdown\n";
}

bool ContractViolationHandler::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::assertions
