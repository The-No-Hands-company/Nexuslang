#include <voltron/utility/testing/test_timeout.h>
#include <iostream>

namespace voltron::utility::testing {

TestTimeout& TestTimeout::instance() {
    static TestTimeout instance;
    return instance;
}

void TestTimeout::initialize() {
    enabled_ = true;
    std::cout << "[TestTimeout] Initialized\n";
}

void TestTimeout::shutdown() {
    enabled_ = false;
    std::cout << "[TestTimeout] Shutdown\n";
}

bool TestTimeout::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::testing
