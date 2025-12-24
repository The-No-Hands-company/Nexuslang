#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::safety {

/**
 * @brief Detect potential failure modes
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Safety
 * @version 1.0.0
 */
class FailureModeDetector {
public:
    /**
     * @brief Get singleton instance
     */
    static FailureModeDetector& instance();

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
    FailureModeDetector() = default;
    ~FailureModeDetector() = default;
    
    // Non-copyable, non-movable
    FailureModeDetector(const FailureModeDetector&) = delete;
    FailureModeDetector& operator=(const FailureModeDetector&) = delete;
    FailureModeDetector(FailureModeDetector&&) = delete;
    FailureModeDetector& operator=(FailureModeDetector&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::safety
