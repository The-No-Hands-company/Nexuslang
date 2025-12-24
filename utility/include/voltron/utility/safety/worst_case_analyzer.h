#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::safety {

/**
 * @brief Perform worst-case timing analysis
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Safety
 * @version 1.0.0
 */
class WorstCaseAnalyzer {
public:
    /**
     * @brief Get singleton instance
     */
    static WorstCaseAnalyzer& instance();

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
    WorstCaseAnalyzer() = default;
    ~WorstCaseAnalyzer() = default;
    
    // Non-copyable, non-movable
    WorstCaseAnalyzer(const WorstCaseAnalyzer&) = delete;
    WorstCaseAnalyzer& operator=(const WorstCaseAnalyzer&) = delete;
    WorstCaseAnalyzer(WorstCaseAnalyzer&&) = delete;
    WorstCaseAnalyzer& operator=(WorstCaseAnalyzer&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::safety
