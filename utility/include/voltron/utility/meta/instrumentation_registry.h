#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::meta {

/**
 * @brief Register all instrumentation points
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Meta
 * @version 1.0.0
 */
class InstrumentationRegistry {
public:
    /**
     * @brief Get singleton instance
     */
    static InstrumentationRegistry& instance();

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
    InstrumentationRegistry() = default;
    ~InstrumentationRegistry() = default;
    
    // Non-copyable, non-movable
    InstrumentationRegistry(const InstrumentationRegistry&) = delete;
    InstrumentationRegistry& operator=(const InstrumentationRegistry&) = delete;
    InstrumentationRegistry(InstrumentationRegistry&&) = delete;
    InstrumentationRegistry& operator=(InstrumentationRegistry&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::meta
