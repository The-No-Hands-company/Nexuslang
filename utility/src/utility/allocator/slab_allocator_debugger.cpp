#include <voltron/utility/allocator/slab_allocator_debugger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::allocator {

SlabAllocatorDebugger& SlabAllocatorDebugger::instance() {
    static SlabAllocatorDebugger instance;
    return instance;
}

void SlabAllocatorDebugger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[SlabAllocatorDebugger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void SlabAllocatorDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[SlabAllocatorDebugger] Shutdown\n";
}

bool SlabAllocatorDebugger::isEnabled() const {
    return enabled_;
}

void SlabAllocatorDebugger::enable() {
    enabled_ = true;
}

void SlabAllocatorDebugger::disable() {
    enabled_ = false;
}

std::string SlabAllocatorDebugger::getStatus() const {
    std::ostringstream oss;
    oss << "SlabAllocatorDebugger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void SlabAllocatorDebugger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::allocator
