#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::specialized {

/**
 * @brief Validate blockchain operations
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Specialized
 * @version 1.0.0
 */
class BlockchainValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static BlockchainValidator& instance();

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
    BlockchainValidator() = default;
    ~BlockchainValidator() = default;
    
    // Non-copyable, non-movable
    BlockchainValidator(const BlockchainValidator&) = delete;
    BlockchainValidator& operator=(const BlockchainValidator&) = delete;
    BlockchainValidator(BlockchainValidator&&) = delete;
    BlockchainValidator& operator=(BlockchainValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::specialized
