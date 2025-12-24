#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::allocator {

/**
 * @brief Validate arena allocator integrity
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Allocator
 * @version 1.0.0
 */
class ArenaValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static ArenaValidator& instance();

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
    ArenaValidator() = default;
    ~ArenaValidator() = default;
    
    // Non-copyable, non-movable
    ArenaValidator(const ArenaValidator&) = delete;
    ArenaValidator& operator=(const ArenaValidator&) = delete;
    ArenaValidator(ArenaValidator&&) = delete;
    ArenaValidator& operator=(ArenaValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::allocator
