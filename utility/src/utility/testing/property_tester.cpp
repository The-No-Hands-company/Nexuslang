#include <voltron/utility/testing/property_tester.h>
#include <iostream>

namespace voltron::utility::testing {

PropertyTester& PropertyTester::instance() {
    static PropertyTester instance;
    return instance;
}

void PropertyTester::initialize() {
    enabled_ = true;
    std::cout << "[PropertyTester] Initialized\n";
}

void PropertyTester::shutdown() {
    enabled_ = false;
    std::cout << "[PropertyTester] Shutdown\n";
}

bool PropertyTester::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::testing
