#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::orchestration {

/**
 * @brief Export diagnostics to external tools
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Orchestration
 * @version 1.0.0
 */
class DiagnosticExportFramework {
public:
    /**
     * @brief Get singleton instance
     */
    static DiagnosticExportFramework& instance();

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
    DiagnosticExportFramework() = default;
    ~DiagnosticExportFramework() = default;
    
    // Non-copyable, non-movable
    DiagnosticExportFramework(const DiagnosticExportFramework&) = delete;
    DiagnosticExportFramework& operator=(const DiagnosticExportFramework&) = delete;
    DiagnosticExportFramework(DiagnosticExportFramework&&) = delete;
    DiagnosticExportFramework& operator=(DiagnosticExportFramework&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::orchestration
