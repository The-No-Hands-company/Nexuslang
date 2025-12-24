#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::apivalidation {

/**
 * @brief Validate printf-style format strings
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Apivalidation
 * @version 1.0.0
 */
class StringFormatValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static StringFormatValidator& instance();

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
    StringFormatValidator() = default;
    ~StringFormatValidator() = default;
    
    // Non-copyable, non-movable
    StringFormatValidator(const StringFormatValidator&) = delete;
    StringFormatValidator& operator=(const StringFormatValidator&) = delete;
    StringFormatValidator(StringFormatValidator&&) = delete;
    StringFormatValidator& operator=(StringFormatValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::apivalidation
