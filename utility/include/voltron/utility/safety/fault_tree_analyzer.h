#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::safety {

/**
 * @brief Analyze fault tree logic
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Safety
 * @version 1.0.0
 */
class FaultTreeAnalyzer {
public:
    /**
     * @brief Get singleton instance
     */
    static FaultTreeAnalyzer& instance();

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
    FaultTreeAnalyzer() = default;
    ~FaultTreeAnalyzer() = default;
    
    // Non-copyable, non-movable
    FaultTreeAnalyzer(const FaultTreeAnalyzer&) = delete;
    FaultTreeAnalyzer& operator=(const FaultTreeAnalyzer&) = delete;
    FaultTreeAnalyzer(FaultTreeAnalyzer&&) = delete;
    FaultTreeAnalyzer& operator=(FaultTreeAnalyzer&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::safety
