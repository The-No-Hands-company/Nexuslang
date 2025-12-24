#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::i18n {

/**
 * @brief Debug locale-specific string sorting
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category I18n
 * @version 1.0.0
 */
class CollationDebugger {
public:
    /**
     * @brief Get singleton instance
     */
    static CollationDebugger& instance();

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
    CollationDebugger() = default;
    ~CollationDebugger() = default;
    
    // Non-copyable, non-movable
    CollationDebugger(const CollationDebugger&) = delete;
    CollationDebugger& operator=(const CollationDebugger&) = delete;
    CollationDebugger(CollationDebugger&&) = delete;
    CollationDebugger& operator=(CollationDebugger&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::i18n
