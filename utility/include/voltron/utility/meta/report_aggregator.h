#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::meta {

/**
 * @brief Aggregate diagnostic reports
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Meta
 * @version 1.0.0
 */
class ReportAggregator {
public:
    /**
     * @brief Get singleton instance
     */
    static ReportAggregator& instance();

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
    ReportAggregator() = default;
    ~ReportAggregator() = default;
    
    // Non-copyable, non-movable
    ReportAggregator(const ReportAggregator&) = delete;
    ReportAggregator& operator=(const ReportAggregator&) = delete;
    ReportAggregator(ReportAggregator&&) = delete;
    ReportAggregator& operator=(ReportAggregator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::meta
