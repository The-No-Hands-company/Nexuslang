#include <voltron/utility/testing/test_data_generator.h>
#include <iostream>

namespace voltron::utility::testing {

TestDataGenerator& TestDataGenerator::instance() {
    static TestDataGenerator instance;
    return instance;
}

void TestDataGenerator::initialize() {
    enabled_ = true;
    std::cout << "[TestDataGenerator] Initialized\n";
}

void TestDataGenerator::shutdown() {
    enabled_ = false;
    std::cout << "[TestDataGenerator] Shutdown\n";
}

bool TestDataGenerator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::testing
