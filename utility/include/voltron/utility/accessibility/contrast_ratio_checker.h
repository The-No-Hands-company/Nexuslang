#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::accessibility {

/**
 * @brief Check color contrast ratios
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Accessibility
 * @version 1.0.0
 */
class ContrastRatioChecker {
public:
    /**
     * @brief Get singleton instance
     */
    static ContrastRatioChecker& instance();

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
    ContrastRatioChecker() = default;
    ~ContrastRatioChecker() = default;
    
    // Non-copyable, non-movable
    ContrastRatioChecker(const ContrastRatioChecker&) = delete;
    ContrastRatioChecker& operator=(const ContrastRatioChecker&) = delete;
    ContrastRatioChecker(ContrastRatioChecker&&) = delete;
    ContrastRatioChecker& operator=(ContrastRatioChecker&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::accessibility
