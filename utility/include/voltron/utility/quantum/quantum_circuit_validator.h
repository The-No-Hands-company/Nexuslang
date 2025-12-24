#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::quantum {

/**
 * @brief Validate quantum circuit logic
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Quantum
 * @version 1.0.0
 */
class QuantumCircuitValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static QuantumCircuitValidator& instance();

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
    QuantumCircuitValidator() = default;
    ~QuantumCircuitValidator() = default;
    
    // Non-copyable, non-movable
    QuantumCircuitValidator(const QuantumCircuitValidator&) = delete;
    QuantumCircuitValidator& operator=(const QuantumCircuitValidator&) = delete;
    QuantumCircuitValidator(QuantumCircuitValidator&&) = delete;
    QuantumCircuitValidator& operator=(QuantumCircuitValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::quantum
