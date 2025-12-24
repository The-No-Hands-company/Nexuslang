#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::string {

/**
 * @brief Track string interning behavior
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category String
 * @version 1.0.0
 */
class StringInterningTracker {
public:
    /**
     * @brief Get singleton instance
     */
    static StringInterningTracker& instance();

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
    StringInterningTracker() = default;
    ~StringInterningTracker() = default;
    
    // Non-copyable, non-movable
    StringInterningTracker(const StringInterningTracker&) = delete;
    StringInterningTracker& operator=(const StringInterningTracker&) = delete;
    StringInterningTracker(StringInterningTracker&&) = delete;
    StringInterningTracker& operator=(StringInterningTracker&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::string
