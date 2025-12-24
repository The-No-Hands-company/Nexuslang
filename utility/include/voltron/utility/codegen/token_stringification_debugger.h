#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::codegen {

/**
 * @brief Debug # and ## macro operators
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Codegen
 * @version 1.0.0
 */
class TokenStringificationDebugger {
public:
    /**
     * @brief Get singleton instance
     */
    static TokenStringificationDebugger& instance();

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
    TokenStringificationDebugger() = default;
    ~TokenStringificationDebugger() = default;
    
    // Non-copyable, non-movable
    TokenStringificationDebugger(const TokenStringificationDebugger&) = delete;
    TokenStringificationDebugger& operator=(const TokenStringificationDebugger&) = delete;
    TokenStringificationDebugger(TokenStringificationDebugger&&) = delete;
    TokenStringificationDebugger& operator=(TokenStringificationDebugger&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::codegen
