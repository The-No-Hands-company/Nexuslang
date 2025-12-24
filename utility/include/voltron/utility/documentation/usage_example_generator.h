#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::documentation {

/**
 * @brief Generate usage examples from code
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Documentation
 * @version 1.0.0
 */
class UsageExampleGenerator {
public:
    /**
     * @brief Get singleton instance
     */
    static UsageExampleGenerator& instance();

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
    UsageExampleGenerator() = default;
    ~UsageExampleGenerator() = default;
    
    // Non-copyable, non-movable
    UsageExampleGenerator(const UsageExampleGenerator&) = delete;
    UsageExampleGenerator& operator=(const UsageExampleGenerator&) = delete;
    UsageExampleGenerator(UsageExampleGenerator&&) = delete;
    UsageExampleGenerator& operator=(UsageExampleGenerator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::documentation
