#pragma once

#include <string>
#include <vector>

namespace voltron::utility::network {

/**
 * @brief Track requests across services
 * 
 * TODO: Implement comprehensive request_id_propagator functionality
 */
class RequestIdPropagator {
public:
    static RequestIdPropagator& instance();

    /**
     * @brief Initialize request_id_propagator
     */
    void initialize();

    /**
     * @brief Shutdown request_id_propagator
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    RequestIdPropagator() = default;
    ~RequestIdPropagator() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::network
