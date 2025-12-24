#pragma once

#include <string>
#include <vector>

namespace voltron::utility::metrics {

/**
 * @brief Export to Prometheus/StatsD
 * 
 * TODO: Implement comprehensive metrics_exporter functionality
 */
class MetricsExporter {
public:
    static MetricsExporter& instance();

    /**
     * @brief Initialize metrics_exporter
     */
    void initialize();

    /**
     * @brief Shutdown metrics_exporter
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    MetricsExporter() = default;
    ~MetricsExporter() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::metrics
