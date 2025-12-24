#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::crossplatform {

/**
 * @brief Detect system endianness
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Crossplatform
 * @version 1.0.0
 */
class EndiannessDetector {
public:
    /**
     * @brief Get singleton instance
     */
    static EndiannessDetector& instance();

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
    EndiannessDetector() = default;
    ~EndiannessDetector() = default;
    
    // Non-copyable, non-movable
    EndiannessDetector(const EndiannessDetector&) = delete;
    EndiannessDetector& operator=(const EndiannessDetector&) = delete;
    EndiannessDetector(EndiannessDetector&&) = delete;
    EndiannessDetector& operator=(EndiannessDetector&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::crossplatform
