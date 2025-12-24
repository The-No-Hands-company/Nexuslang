#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::interop {

/**
 * @brief Debug Java Native Interface calls
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Interop
 * @version 1.0.0
 */
class JniHelperDebug {
public:
    /**
     * @brief Get singleton instance
     */
    static JniHelperDebug& instance();

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
    JniHelperDebug() = default;
    ~JniHelperDebug() = default;
    
    // Non-copyable, non-movable
    JniHelperDebug(const JniHelperDebug&) = delete;
    JniHelperDebug& operator=(const JniHelperDebug&) = delete;
    JniHelperDebug(JniHelperDebug&&) = delete;
    JniHelperDebug& operator=(JniHelperDebug&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::interop
