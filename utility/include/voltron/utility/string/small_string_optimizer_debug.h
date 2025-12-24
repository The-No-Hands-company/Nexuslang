#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::string {

/**
 * @brief Debug small string optimization
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category String
 * @version 1.0.0
 */
class SmallStringOptimizerDebug {
public:
    /**
     * @brief Get singleton instance
     */
    static SmallStringOptimizerDebug& instance();

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
    SmallStringOptimizerDebug() = default;
    ~SmallStringOptimizerDebug() = default;
    
    // Non-copyable, non-movable
    SmallStringOptimizerDebug(const SmallStringOptimizerDebug&) = delete;
    SmallStringOptimizerDebug& operator=(const SmallStringOptimizerDebug&) = delete;
    SmallStringOptimizerDebug(SmallStringOptimizerDebug&&) = delete;
    SmallStringOptimizerDebug& operator=(SmallStringOptimizerDebug&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::string
