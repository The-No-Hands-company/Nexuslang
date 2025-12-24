#pragma once

#include <string>
#include <vector>

namespace voltron::utility::statemachine {

/**
 * @brief Log all events for replay
 * 
 * TODO: Implement comprehensive event_sourcing_logger functionality
 */
class EventSourcingLogger {
public:
    static EventSourcingLogger& instance();

    /**
     * @brief Initialize event_sourcing_logger
     */
    void initialize();

    /**
     * @brief Shutdown event_sourcing_logger
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    EventSourcingLogger() = default;
    ~EventSourcingLogger() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::statemachine
