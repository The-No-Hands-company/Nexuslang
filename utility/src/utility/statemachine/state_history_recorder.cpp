#include <voltron/utility/statemachine/state_history_recorder.h>
#include <iostream>

namespace voltron::utility::statemachine {

StateHistoryRecorder& StateHistoryRecorder::instance() {
    static StateHistoryRecorder instance;
    return instance;
}

void StateHistoryRecorder::initialize() {
    enabled_ = true;
    std::cout << "[StateHistoryRecorder] Initialized\n";
}

void StateHistoryRecorder::shutdown() {
    enabled_ = false;
    std::cout << "[StateHistoryRecorder] Shutdown\n";
}

bool StateHistoryRecorder::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::statemachine
