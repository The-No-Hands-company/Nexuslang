#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::orchestration {

/**
 * @brief Correlate events across systems
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Orchestration
 * @version 1.0.0
 */
class CrossSystemCorrelator {
public:
    /**
     * @brief Get singleton instance
     */
    static CrossSystemCorrelator& instance();

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
    CrossSystemCorrelator() = default;
    ~CrossSystemCorrelator() = default;
    
    // Non-copyable, non-movable
    CrossSystemCorrelator(const CrossSystemCorrelator&) = delete;
    CrossSystemCorrelator& operator=(const CrossSystemCorrelator&) = delete;
    CrossSystemCorrelator(CrossSystemCorrelator&&) = delete;
    CrossSystemCorrelator& operator=(CrossSystemCorrelator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::orchestration
