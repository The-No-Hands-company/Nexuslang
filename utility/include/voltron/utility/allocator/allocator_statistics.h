#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::allocator {

/**
 * @brief Collect allocator performance statistics
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Allocator
 * @version 1.0.0
 */
class AllocatorStatistics {
public:
    /**
     * @brief Get singleton instance
     */
    static AllocatorStatistics& instance();

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
    AllocatorStatistics() = default;
    ~AllocatorStatistics() = default;
    
    // Non-copyable, non-movable
    AllocatorStatistics(const AllocatorStatistics&) = delete;
    AllocatorStatistics& operator=(const AllocatorStatistics&) = delete;
    AllocatorStatistics(AllocatorStatistics&&) = delete;
    AllocatorStatistics& operator=(AllocatorStatistics&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::allocator
