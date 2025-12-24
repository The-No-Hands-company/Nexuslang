#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::gamedev {

/**
 * @brief Validate animation state machines
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Gamedev
 * @version 1.0.0
 */
class AnimationValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static AnimationValidator& instance();

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
    AnimationValidator() = default;
    ~AnimationValidator() = default;
    
    // Non-copyable, non-movable
    AnimationValidator(const AnimationValidator&) = delete;
    AnimationValidator& operator=(const AnimationValidator&) = delete;
    AnimationValidator(AnimationValidator&&) = delete;
    AnimationValidator& operator=(AnimationValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::gamedev
