#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::gamedev {

/**
 * @brief Debug networked game synchronization
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Gamedev
 * @version 1.0.0
 */
class NetcodeDebugger {
public:
    /**
     * @brief Get singleton instance
     */
    static NetcodeDebugger& instance();

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
    NetcodeDebugger() = default;
    ~NetcodeDebugger() = default;
    
    // Non-copyable, non-movable
    NetcodeDebugger(const NetcodeDebugger&) = delete;
    NetcodeDebugger& operator=(const NetcodeDebugger&) = delete;
    NetcodeDebugger(NetcodeDebugger&&) = delete;
    NetcodeDebugger& operator=(NetcodeDebugger&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::gamedev
