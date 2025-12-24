#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::orchestration {

/**
 * @brief Automated issue remediation
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Orchestration
 * @version 1.0.0
 */
class AutomatedRemediation {
public:
    /**
     * @brief Get singleton instance
     */
    static AutomatedRemediation& instance();

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
    AutomatedRemediation() = default;
    ~AutomatedRemediation() = default;
    
    // Non-copyable, non-movable
    AutomatedRemediation(const AutomatedRemediation&) = delete;
    AutomatedRemediation& operator=(const AutomatedRemediation&) = delete;
    AutomatedRemediation(AutomatedRemediation&&) = delete;
    AutomatedRemediation& operator=(AutomatedRemediation&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::orchestration
