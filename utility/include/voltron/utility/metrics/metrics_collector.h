#pragma once

#include <string>
#include <vector>

namespace voltron::utility::metrics {

/**
 * @brief Collect runtime metrics
 * 
 * TODO: Implement comprehensive metrics_collector functionality
 */
class MetricsCollector {
public:
    static MetricsCollector& instance();

    /**
     * @brief Initialize metrics_collector
     */
    void initialize();

    /**
     * @brief Shutdown metrics_collector
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    MetricsCollector() = default;
    ~MetricsCollector() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::metrics
