#include <voltron/utility/gamedev/input_replay_recorder.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::gamedev {

InputReplayRecorder& InputReplayRecorder::instance() {
    static InputReplayRecorder instance;
    return instance;
}

void InputReplayRecorder::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[InputReplayRecorder] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void InputReplayRecorder::shutdown() {
    enabled_ = false;
    std::cout << "[InputReplayRecorder] Shutdown\n";
}

bool InputReplayRecorder::isEnabled() const {
    return enabled_;
}

void InputReplayRecorder::enable() {
    enabled_ = true;
}

void InputReplayRecorder::disable() {
    enabled_ = false;
}

std::string InputReplayRecorder::getStatus() const {
    std::ostringstream oss;
    oss << "InputReplayRecorder - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void InputReplayRecorder::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::gamedev
