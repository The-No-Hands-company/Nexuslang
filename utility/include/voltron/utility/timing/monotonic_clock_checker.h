#pragma once

#include <string>
#include <vector>

namespace voltron::utility::timing {

/**
 * @brief Ensure monotonic time
 * 
 * TODO: Implement comprehensive monotonic_clock_checker functionality
 */
class MonotonicClockChecker {
public:
    static MonotonicClockChecker& instance();

    /**
     * @brief Initialize monotonic_clock_checker
     */
    void initialize();

    /**
     * @brief Shutdown monotonic_clock_checker
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    MonotonicClockChecker() = default;
    ~MonotonicClockChecker() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::timing
