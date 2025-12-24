#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::allocator {

/**
 * @brief Profile garbage collection
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Allocator
 * @version 1.0.0
 */
class GarbageCollectorProfiler {
public:
    /**
     * @brief Get singleton instance
     */
    static GarbageCollectorProfiler& instance();

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
    GarbageCollectorProfiler() = default;
    ~GarbageCollectorProfiler() = default;
    
    // Non-copyable, non-movable
    GarbageCollectorProfiler(const GarbageCollectorProfiler&) = delete;
    GarbageCollectorProfiler& operator=(const GarbageCollectorProfiler&) = delete;
    GarbageCollectorProfiler(GarbageCollectorProfiler&&) = delete;
    GarbageCollectorProfiler& operator=(GarbageCollectorProfiler&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::allocator
