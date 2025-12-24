#pragma once

#include <string>
#include <vector>

namespace voltron::utility::metrics {

/**
 * @brief Current value tracking
 * 
 * TODO: Implement comprehensive gauge functionality
 */
class Gauge {
public:
    static Gauge& instance();

    /**
     * @brief Initialize gauge
     */
    void initialize();

    /**
     * @brief Shutdown gauge
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    Gauge() = default;
    ~Gauge() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::metrics
