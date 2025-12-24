#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::financial {

/**
 * @brief Validate tick size precision
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Financial
 * @version 1.0.0
 */
class TickPrecisionValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static TickPrecisionValidator& instance();

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
    TickPrecisionValidator() = default;
    ~TickPrecisionValidator() = default;
    
    // Non-copyable, non-movable
    TickPrecisionValidator(const TickPrecisionValidator&) = delete;
    TickPrecisionValidator& operator=(const TickPrecisionValidator&) = delete;
    TickPrecisionValidator(TickPrecisionValidator&&) = delete;
    TickPrecisionValidator& operator=(TickPrecisionValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::financial
