#pragma once

#include <string>
#include <vector>

namespace voltron::utility::statemachine {

/**
 * @brief Track multi-step workflows
 * 
 * TODO: Implement comprehensive workflow_tracker functionality
 */
class WorkflowTracker {
public:
    static WorkflowTracker& instance();

    /**
     * @brief Initialize workflow_tracker
     */
    void initialize();

    /**
     * @brief Shutdown workflow_tracker
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    WorkflowTracker() = default;
    ~WorkflowTracker() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::statemachine
