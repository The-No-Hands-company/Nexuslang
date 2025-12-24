#include <voltron/utility/formal/loop_invariant_helper.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::formal {

LoopInvariantHelper& LoopInvariantHelper::instance() {
    static LoopInvariantHelper instance;
    return instance;
}

void LoopInvariantHelper::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[LoopInvariantHelper] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void LoopInvariantHelper::shutdown() {
    enabled_ = false;
    std::cout << "[LoopInvariantHelper] Shutdown\n";
}

bool LoopInvariantHelper::isEnabled() const {
    return enabled_;
}

void LoopInvariantHelper::enable() {
    enabled_ = true;
}

void LoopInvariantHelper::disable() {
    enabled_ = false;
}

std::string LoopInvariantHelper::getStatus() const {
    std::ostringstream oss;
    oss << "LoopInvariantHelper - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void LoopInvariantHelper::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::formal
