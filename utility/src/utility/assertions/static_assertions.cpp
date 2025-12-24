#include <voltron/utility/assertions/static_assertions.h>
#include <iostream>

namespace voltron::utility::assertions {

StaticAssertions& StaticAssertions::instance() {
    static StaticAssertions instance;
    return instance;
}

void StaticAssertions::initialize() {
    enabled_ = true;
    std::cout << "[StaticAssertions] Initialized\n";
}

void StaticAssertions::shutdown() {
    enabled_ = false;
    std::cout << "[StaticAssertions] Shutdown\n";
}

bool StaticAssertions::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::assertions
