#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::meta {

/**
 * @brief Global error handling coordinator
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Meta
 * @version 1.0.0
 */
class GlobalErrorHandler {
public:
    /**
     * @brief Get singleton instance
     */
    static GlobalErrorHandler& instance();

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
    GlobalErrorHandler() = default;
    ~GlobalErrorHandler() = default;
    
    // Non-copyable, non-movable
    GlobalErrorHandler(const GlobalErrorHandler&) = delete;
    GlobalErrorHandler& operator=(const GlobalErrorHandler&) = delete;
    GlobalErrorHandler(GlobalErrorHandler&&) = delete;
    GlobalErrorHandler& operator=(GlobalErrorHandler&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::meta
