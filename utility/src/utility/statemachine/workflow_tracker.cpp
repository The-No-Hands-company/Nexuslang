#include <voltron/utility/statemachine/workflow_tracker.h>
#include <iostream>

namespace voltron::utility::statemachine {

WorkflowTracker& WorkflowTracker::instance() {
    static WorkflowTracker instance;
    return instance;
}

void WorkflowTracker::initialize() {
    enabled_ = true;
    std::cout << "[WorkflowTracker] Initialized\n";
}

void WorkflowTracker::shutdown() {
    enabled_ = false;
    std::cout << "[WorkflowTracker] Shutdown\n";
}

bool WorkflowTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::statemachine
