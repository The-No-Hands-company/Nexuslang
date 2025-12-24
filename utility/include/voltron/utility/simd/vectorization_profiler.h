#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::simd {

/**
 * @brief Profile SIMD vectorization
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Simd
 * @version 1.0.0
 */
class VectorizationProfiler {
public:
    /**
     * @brief Get singleton instance
     */
    static VectorizationProfiler& instance();

    /**
     * @brief Initialize the utility
     * @param config Optional configuration parameters
     */
    void initialize(const std::string& config = "");

    /**
     * @brief Shutdown the utility and cleanup resources
     */
    void shutdown();

    /**
     * @brief Check if the utility is currently enabled
     */
    bool isEnabled() const;

    /**
     * @brief Enable the utility
     */
    void enable();

    /**
     * @brief Disable the utility
     */
    void disable();

    /**
     * @brief Get utility statistics/status
     */
    std::string getStatus() const;

    /**
     * @brief Reset utility state
     */
    void reset();

private:
    VectorizationProfiler() = default;
    ~VectorizationProfiler() = default;
    
    // Non-copyable, non-movable
    VectorizationProfiler(const VectorizationProfiler&) = delete;
    VectorizationProfiler& operator=(const VectorizationProfiler&) = delete;
    VectorizationProfiler(VectorizationProfiler&&) = delete;
    VectorizationProfiler& operator=(VectorizationProfiler&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::simd
