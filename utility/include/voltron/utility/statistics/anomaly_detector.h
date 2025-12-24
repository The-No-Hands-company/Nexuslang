#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::statistics {

/**
 * @brief Detect behavioral anomalies
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Statistics
 * @version 1.0.0
 */
class AnomalyDetector {
public:
    /**
     * @brief Get singleton instance
     */
    static AnomalyDetector& instance();

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
    AnomalyDetector() = default;
    ~AnomalyDetector() = default;
    
    // Non-copyable, non-movable
    AnomalyDetector(const AnomalyDetector&) = delete;
    AnomalyDetector& operator=(const AnomalyDetector&) = delete;
    AnomalyDetector(AnomalyDetector&&) = delete;
    AnomalyDetector& operator=(AnomalyDetector&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::statistics
