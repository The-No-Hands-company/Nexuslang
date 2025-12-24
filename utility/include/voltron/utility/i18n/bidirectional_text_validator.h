#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::i18n {

/**
 * @brief Validate bidirectional text handling
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category I18n
 * @version 1.0.0
 */
class BidirectionalTextValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static BidirectionalTextValidator& instance();

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
    BidirectionalTextValidator() = default;
    ~BidirectionalTextValidator() = default;
    
    // Non-copyable, non-movable
    BidirectionalTextValidator(const BidirectionalTextValidator&) = delete;
    BidirectionalTextValidator& operator=(const BidirectionalTextValidator&) = delete;
    BidirectionalTextValidator(BidirectionalTextValidator&&) = delete;
    BidirectionalTextValidator& operator=(BidirectionalTextValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::i18n
