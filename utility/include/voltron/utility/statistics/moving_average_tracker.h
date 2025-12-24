#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::statistics {

/**
 * @brief Track moving average metrics
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Statistics
 * @version 1.0.0
 */
class MovingAverageTracker {
public:
    /**
     * @brief Get singleton instance
     */
    static MovingAverageTracker& instance();

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
    MovingAverageTracker() = default;
    ~MovingAverageTracker() = default;
    
    // Non-copyable, non-movable
    MovingAverageTracker(const MovingAverageTracker&) = delete;
    MovingAverageTracker& operator=(const MovingAverageTracker&) = delete;
    MovingAverageTracker(MovingAverageTracker&&) = delete;
    MovingAverageTracker& operator=(MovingAverageTracker&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::statistics
