#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::scientific {

/**
 * @brief Diagnose iterative solver issues
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Scientific
 * @version 1.0.0
 */
class SolverDiagnostics {
public:
    /**
     * @brief Get singleton instance
     */
    static SolverDiagnostics& instance();

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
    SolverDiagnostics() = default;
    ~SolverDiagnostics() = default;
    
    // Non-copyable, non-movable
    SolverDiagnostics(const SolverDiagnostics&) = delete;
    SolverDiagnostics& operator=(const SolverDiagnostics&) = delete;
    SolverDiagnostics(SolverDiagnostics&&) = delete;
    SolverDiagnostics& operator=(SolverDiagnostics&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::scientific
