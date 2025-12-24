#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::financial {

/**
 * @brief Ensure decimal arithmetic precision
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Financial
 * @version 1.0.0
 */
class DecimalPrecisionValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static DecimalPrecisionValidator& instance();

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
    DecimalPrecisionValidator() = default;
    ~DecimalPrecisionValidator() = default;
    
    // Non-copyable, non-movable
    DecimalPrecisionValidator(const DecimalPrecisionValidator&) = delete;
    DecimalPrecisionValidator& operator=(const DecimalPrecisionValidator&) = delete;
    DecimalPrecisionValidator(DecimalPrecisionValidator&&) = delete;
    DecimalPrecisionValidator& operator=(DecimalPrecisionValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::financial
