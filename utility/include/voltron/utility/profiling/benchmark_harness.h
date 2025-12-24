#pragma once

#include <string>
#include <vector>

namespace voltron::utility::profiling {

/**
 * @brief Microbenchmarking utilities
 * 
 * TODO: Implement comprehensive benchmark_harness functionality
 */
class BenchmarkHarness {
public:
    static BenchmarkHarness& instance();

    /**
     * @brief Initialize benchmark_harness
     */
    void initialize();

    /**
     * @brief Shutdown benchmark_harness
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    BenchmarkHarness() = default;
    ~BenchmarkHarness() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::profiling
