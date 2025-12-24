#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::quantum {

/**
 * @brief Track quantum error correction
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Quantum
 * @version 1.0.0
 */
class QuantumErrorCorrector {
public:
    /**
     * @brief Get singleton instance
     */
    static QuantumErrorCorrector& instance();

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
    QuantumErrorCorrector() = default;
    ~QuantumErrorCorrector() = default;
    
    // Non-copyable, non-movable
    QuantumErrorCorrector(const QuantumErrorCorrector&) = delete;
    QuantumErrorCorrector& operator=(const QuantumErrorCorrector&) = delete;
    QuantumErrorCorrector(QuantumErrorCorrector&&) = delete;
    QuantumErrorCorrector& operator=(QuantumErrorCorrector&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::quantum
