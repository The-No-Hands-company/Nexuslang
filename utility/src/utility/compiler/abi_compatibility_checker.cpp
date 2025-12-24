#include <voltron/utility/compiler/abi_compatibility_checker.h>
#include <iostream>

namespace voltron::utility::compiler {

AbiCompatibilityChecker& AbiCompatibilityChecker::instance() {
    static AbiCompatibilityChecker instance;
    return instance;
}

void AbiCompatibilityChecker::initialize() {
    enabled_ = true;
    std::cout << "[AbiCompatibilityChecker] Initialized\n";
}

void AbiCompatibilityChecker::shutdown() {
    enabled_ = false;
    std::cout << "[AbiCompatibilityChecker] Shutdown\n";
}

bool AbiCompatibilityChecker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::compiler
