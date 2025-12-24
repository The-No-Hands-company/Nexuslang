#include <voltron/utility/testing/mock_generator.h>
#include <iostream>

namespace voltron::utility::testing {

MockGenerator& MockGenerator::instance() {
    static MockGenerator instance;
    return instance;
}

void MockGenerator::initialize() {
    enabled_ = true;
    std::cout << "[MockGenerator] Initialized\n";
}

void MockGenerator::shutdown() {
    enabled_ = false;
    std::cout << "[MockGenerator] Shutdown\n";
}

bool MockGenerator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::testing
