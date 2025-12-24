#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::formal {

/**
 * @brief Support symbolic execution analysis
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Formal
 * @version 1.0.0
 */
class SymbolicExecutionHelper {
public:
    /**
     * @brief Get singleton instance
     */
    static SymbolicExecutionHelper& instance();

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
    SymbolicExecutionHelper() = default;
    ~SymbolicExecutionHelper() = default;
    
    // Non-copyable, non-movable
    SymbolicExecutionHelper(const SymbolicExecutionHelper&) = delete;
    SymbolicExecutionHelper& operator=(const SymbolicExecutionHelper&) = delete;
    SymbolicExecutionHelper(SymbolicExecutionHelper&&) = delete;
    SymbolicExecutionHelper& operator=(SymbolicExecutionHelper&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::formal
