#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::container {

/**
 * @brief Validate seccomp security profiles
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Container
 * @version 1.0.0
 */
class SeccompValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static SeccompValidator& instance();

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
    SeccompValidator() = default;
    ~SeccompValidator() = default;
    
    // Non-copyable, non-movable
    SeccompValidator(const SeccompValidator&) = delete;
    SeccompValidator& operator=(const SeccompValidator&) = delete;
    SeccompValidator(SeccompValidator&&) = delete;
    SeccompValidator& operator=(SeccompValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::container
