#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::string {

/**
 * @brief Validate case folding operations
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category String
 * @version 1.0.0
 */
class CaseFoldingValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static CaseFoldingValidator& instance();

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
    CaseFoldingValidator() = default;
    ~CaseFoldingValidator() = default;
    
    // Non-copyable, non-movable
    CaseFoldingValidator(const CaseFoldingValidator&) = delete;
    CaseFoldingValidator& operator=(const CaseFoldingValidator&) = delete;
    CaseFoldingValidator(CaseFoldingValidator&&) = delete;
    CaseFoldingValidator& operator=(CaseFoldingValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::string
