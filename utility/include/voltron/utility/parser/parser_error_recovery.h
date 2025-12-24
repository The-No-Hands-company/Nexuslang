#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::parser {

/**
 * @brief Debug parser error recovery
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Parser
 * @version 1.0.0
 */
class ParserErrorRecovery {
public:
    /**
     * @brief Get singleton instance
     */
    static ParserErrorRecovery& instance();

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
    ParserErrorRecovery() = default;
    ~ParserErrorRecovery() = default;
    
    // Non-copyable, non-movable
    ParserErrorRecovery(const ParserErrorRecovery&) = delete;
    ParserErrorRecovery& operator=(const ParserErrorRecovery&) = delete;
    ParserErrorRecovery(ParserErrorRecovery&&) = delete;
    ParserErrorRecovery& operator=(ParserErrorRecovery&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::parser
