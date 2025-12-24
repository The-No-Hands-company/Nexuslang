#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::protocol {

/**
 * @brief Fuzz test protocol implementations
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Protocol
 * @version 1.0.0
 */
class ProtocolFuzzer {
public:
    /**
     * @brief Get singleton instance
     */
    static ProtocolFuzzer& instance();

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
    ProtocolFuzzer() = default;
    ~ProtocolFuzzer() = default;
    
    // Non-copyable, non-movable
    ProtocolFuzzer(const ProtocolFuzzer&) = delete;
    ProtocolFuzzer& operator=(const ProtocolFuzzer&) = delete;
    ProtocolFuzzer(ProtocolFuzzer&&) = delete;
    ProtocolFuzzer& operator=(ProtocolFuzzer&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::protocol
