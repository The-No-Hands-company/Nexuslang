#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::apivalidation {

/**
 * @brief Warn about deprecated API usage
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Apivalidation
 * @version 1.0.0
 */
class DeprecationWarner {
public:
    /**
     * @brief Get singleton instance
     */
    static DeprecationWarner& instance();

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
    DeprecationWarner() = default;
    ~DeprecationWarner() = default;
    
    // Non-copyable, non-movable
    DeprecationWarner(const DeprecationWarner&) = delete;
    DeprecationWarner& operator=(const DeprecationWarner&) = delete;
    DeprecationWarner(DeprecationWarner&&) = delete;
    DeprecationWarner& operator=(DeprecationWarner&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::apivalidation
