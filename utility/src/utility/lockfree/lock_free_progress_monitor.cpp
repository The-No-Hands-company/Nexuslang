#include <voltron/utility/lockfree/lock_free_progress_monitor.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::lockfree {

LockFreeProgressMonitor& LockFreeProgressMonitor::instance() {
    static LockFreeProgressMonitor instance;
    return instance;
}

void LockFreeProgressMonitor::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[LockFreeProgressMonitor] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void LockFreeProgressMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[LockFreeProgressMonitor] Shutdown\n";
}

bool LockFreeProgressMonitor::isEnabled() const {
    return enabled_;
}

void LockFreeProgressMonitor::enable() {
    enabled_ = true;
}

void LockFreeProgressMonitor::disable() {
    enabled_ = false;
}

std::string LockFreeProgressMonitor::getStatus() const {
    std::ostringstream oss;
    oss << "LockFreeProgressMonitor - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void LockFreeProgressMonitor::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::lockfree
