#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::meta {

/**
 * @brief Initialize all diagnostic systems
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Meta
 * @version 1.0.0
 */
class DiagnosticsInitializer {
public:
    /**
     * @brief Get singleton instance
     */
    static DiagnosticsInitializer& instance();

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
    DiagnosticsInitializer() = default;
    ~DiagnosticsInitializer() = default;
    
    // Non-copyable, non-movable
    DiagnosticsInitializer(const DiagnosticsInitializer&) = delete;
    DiagnosticsInitializer& operator=(const DiagnosticsInitializer&) = delete;
    DiagnosticsInitializer(DiagnosticsInitializer&&) = delete;
    DiagnosticsInitializer& operator=(DiagnosticsInitializer&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::meta
