#include <voltron/utility/profiling/benchmark_harness.h>
#include <iostream>

namespace voltron::utility::profiling {

BenchmarkHarness& BenchmarkHarness::instance() {
    static BenchmarkHarness instance;
    return instance;
}

void BenchmarkHarness::initialize() {
    enabled_ = true;
    std::cout << "[BenchmarkHarness] Initialized\n";
}

void BenchmarkHarness::shutdown() {
    enabled_ = false;
    std::cout << "[BenchmarkHarness] Shutdown\n";
}

bool BenchmarkHarness::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::profiling
