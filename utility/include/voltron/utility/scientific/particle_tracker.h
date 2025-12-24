#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::scientific {

/**
 * @brief Debug particle-based simulations
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Scientific
 * @version 1.0.0
 */
class ParticleTracker {
public:
    /**
     * @brief Get singleton instance
     */
    static ParticleTracker& instance();

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
    ParticleTracker() = default;
    ~ParticleTracker() = default;
    
    // Non-copyable, non-movable
    ParticleTracker(const ParticleTracker&) = delete;
    ParticleTracker& operator=(const ParticleTracker&) = delete;
    ParticleTracker(ParticleTracker&&) = delete;
    ParticleTracker& operator=(ParticleTracker&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::scientific
