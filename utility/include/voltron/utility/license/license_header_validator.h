#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::license {

/**
 * @brief Ensure proper license file headers
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category License
 * @version 1.0.0
 */
class LicenseHeaderValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static LicenseHeaderValidator& instance();

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
    LicenseHeaderValidator() = default;
    ~LicenseHeaderValidator() = default;
    
    // Non-copyable, non-movable
    LicenseHeaderValidator(const LicenseHeaderValidator&) = delete;
    LicenseHeaderValidator& operator=(const LicenseHeaderValidator&) = delete;
    LicenseHeaderValidator(LicenseHeaderValidator&&) = delete;
    LicenseHeaderValidator& operator=(LicenseHeaderValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::license
