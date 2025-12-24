#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::hardware {

/**
 * @brief Validate hardware sensor readings
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Hardware
 * @version 1.0.0
 */
class SensorValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static SensorValidator& instance();

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
    SensorValidator() = default;
    ~SensorValidator() = default;
    
    // Non-copyable, non-movable
    SensorValidator(const SensorValidator&) = delete;
    SensorValidator& operator=(const SensorValidator&) = delete;
    SensorValidator(SensorValidator&&) = delete;
    SensorValidator& operator=(SensorValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::hardware
