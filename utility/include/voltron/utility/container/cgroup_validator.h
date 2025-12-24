#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::container {

/**
 * @brief Validate cgroup configuration
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Container
 * @version 1.0.0
 */
class CgroupValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static CgroupValidator& instance();

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
    CgroupValidator() = default;
    ~CgroupValidator() = default;
    
    // Non-copyable, non-movable
    CgroupValidator(const CgroupValidator&) = delete;
    CgroupValidator& operator=(const CgroupValidator&) = delete;
    CgroupValidator(CgroupValidator&&) = delete;
    CgroupValidator& operator=(CgroupValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::container
