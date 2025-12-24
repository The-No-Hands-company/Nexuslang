#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::gamedev {

/**
 * @brief Visualize spatial partitioning
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Gamedev
 * @version 1.0.0
 */
class SpatialPartitionVisualizer {
public:
    /**
     * @brief Get singleton instance
     */
    static SpatialPartitionVisualizer& instance();

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
    SpatialPartitionVisualizer() = default;
    ~SpatialPartitionVisualizer() = default;
    
    // Non-copyable, non-movable
    SpatialPartitionVisualizer(const SpatialPartitionVisualizer&) = delete;
    SpatialPartitionVisualizer& operator=(const SpatialPartitionVisualizer&) = delete;
    SpatialPartitionVisualizer(SpatialPartitionVisualizer&&) = delete;
    SpatialPartitionVisualizer& operator=(SpatialPartitionVisualizer&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::gamedev
