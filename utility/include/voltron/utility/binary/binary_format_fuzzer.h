#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::binary {

/**
 * @brief Fuzz test binary format parsers
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Binary
 * @version 1.0.0
 */
class BinaryFormatFuzzer {
public:
    /**
     * @brief Get singleton instance
     */
    static BinaryFormatFuzzer& instance();

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
    BinaryFormatFuzzer() = default;
    ~BinaryFormatFuzzer() = default;
    
    // Non-copyable, non-movable
    BinaryFormatFuzzer(const BinaryFormatFuzzer&) = delete;
    BinaryFormatFuzzer& operator=(const BinaryFormatFuzzer&) = delete;
    BinaryFormatFuzzer(BinaryFormatFuzzer&&) = delete;
    BinaryFormatFuzzer& operator=(BinaryFormatFuzzer&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::binary
