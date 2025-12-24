#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::accessibility {

/**
 * @brief Validate ARIA accessibility attributes
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Accessibility
 * @version 1.0.0
 */
class AriaAttributeValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static AriaAttributeValidator& instance();

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
    AriaAttributeValidator() = default;
    ~AriaAttributeValidator() = default;
    
    // Non-copyable, non-movable
    AriaAttributeValidator(const AriaAttributeValidator&) = delete;
    AriaAttributeValidator& operator=(const AriaAttributeValidator&) = delete;
    AriaAttributeValidator(AriaAttributeValidator&&) = delete;
    AriaAttributeValidator& operator=(AriaAttributeValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::accessibility
