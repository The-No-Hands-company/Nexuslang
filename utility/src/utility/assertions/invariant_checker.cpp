#include <voltron/utility/assertions/invariant_checker.h>
#include <iostream>

namespace voltron::utility::assertions {

InvariantChecker& InvariantChecker::instance() {
    static InvariantChecker instance;
    return instance;
}

void InvariantChecker::initialize() {
    enabled_ = true;
    std::cout << "[InvariantChecker] Initialized\n";
}

void InvariantChecker::shutdown() {
    enabled_ = false;
    std::cout << "[InvariantChecker] Shutdown\n";
}

bool InvariantChecker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::assertions
