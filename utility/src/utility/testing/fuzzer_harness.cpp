#include <voltron/utility/testing/fuzzer_harness.h>
#include <iostream>

namespace voltron::utility::testing {

FuzzerHarness& FuzzerHarness::instance() {
    static FuzzerHarness instance;
    return instance;
}

void FuzzerHarness::initialize() {
    enabled_ = true;
    std::cout << "[FuzzerHarness] Initialized\n";
}

void FuzzerHarness::shutdown() {
    enabled_ = false;
    std::cout << "[FuzzerHarness] Shutdown\n";
}

bool FuzzerHarness::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::testing
