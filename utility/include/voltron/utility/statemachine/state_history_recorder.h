#pragma once

#include <string>
#include <vector>

namespace voltron::utility::statemachine {

/**
 * @brief Record state change history
 * 
 * TODO: Implement comprehensive state_history_recorder functionality
 */
class StateHistoryRecorder {
public:
    static StateHistoryRecorder& instance();

    /**
     * @brief Initialize state_history_recorder
     */
    void initialize();

    /**
     * @brief Shutdown state_history_recorder
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    StateHistoryRecorder() = default;
    ~StateHistoryRecorder() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::statemachine
