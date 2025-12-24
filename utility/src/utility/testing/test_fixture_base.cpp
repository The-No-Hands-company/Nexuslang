#include <voltron/utility/testing/test_fixture_base.h>
#include <iostream>

namespace voltron::utility::testing {

TestFixtureBase& TestFixtureBase::instance() {
    static TestFixtureBase instance;
    return instance;
}

void TestFixtureBase::initialize() {
    enabled_ = true;
    std::cout << "[TestFixtureBase] Initialized\n";
}

void TestFixtureBase::shutdown() {
    enabled_ = false;
    std::cout << "[TestFixtureBase] Shutdown\n";
}

bool TestFixtureBase::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::testing
