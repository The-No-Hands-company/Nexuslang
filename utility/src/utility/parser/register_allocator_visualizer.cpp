#include <voltron/utility/parser/register_allocator_visualizer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::parser {

RegisterAllocatorVisualizer& RegisterAllocatorVisualizer::instance() {
    static RegisterAllocatorVisualizer instance;
    return instance;
}

void RegisterAllocatorVisualizer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[RegisterAllocatorVisualizer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void RegisterAllocatorVisualizer::shutdown() {
    enabled_ = false;
    std::cout << "[RegisterAllocatorVisualizer] Shutdown\n";
}

bool RegisterAllocatorVisualizer::isEnabled() const {
    return enabled_;
}

void RegisterAllocatorVisualizer::enable() {
    enabled_ = true;
}

void RegisterAllocatorVisualizer::disable() {
    enabled_ = false;
}

std::string RegisterAllocatorVisualizer::getStatus() const {
    std::ostringstream oss;
    oss << "RegisterAllocatorVisualizer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void RegisterAllocatorVisualizer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::parser
