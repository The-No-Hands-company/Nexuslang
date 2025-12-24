#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::workflow {

/**
 * @brief Mark and track technical debt
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Workflow
 * @version 1.0.0
 */
class TechDebtMarker {
public:
    /**
     * @brief Get singleton instance
     */
    static TechDebtMarker& instance();

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
    TechDebtMarker() = default;
    ~TechDebtMarker() = default;
    
    // Non-copyable, non-movable
    TechDebtMarker(const TechDebtMarker&) = delete;
    TechDebtMarker& operator=(const TechDebtMarker&) = delete;
    TechDebtMarker(TechDebtMarker&&) = delete;
    TechDebtMarker& operator=(TechDebtMarker&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::workflow
