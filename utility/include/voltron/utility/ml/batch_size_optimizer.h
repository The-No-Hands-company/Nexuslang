#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::ml {

/**
 * @brief Track and optimize batch sizes
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Ml
 * @version 1.0.0
 */
class BatchSizeOptimizer {
public:
    /**
     * @brief Get singleton instance
     */
    static BatchSizeOptimizer& instance();

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
    BatchSizeOptimizer() = default;
    ~BatchSizeOptimizer() = default;
    
    // Non-copyable, non-movable
    BatchSizeOptimizer(const BatchSizeOptimizer&) = delete;
    BatchSizeOptimizer& operator=(const BatchSizeOptimizer&) = delete;
    BatchSizeOptimizer(BatchSizeOptimizer&&) = delete;
    BatchSizeOptimizer& operator=(BatchSizeOptimizer&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::ml
