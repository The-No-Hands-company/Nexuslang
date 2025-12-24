#include "voltron/utility/memory/double_free_detector.h"
#include <iostream>

namespace voltron::utility::memory {

DoubleFreeDetector& DoubleFreeDetector::instance() {
    static DoubleFreeDetector detector;
    return detector;
}

void DoubleFreeDetector::recordFree(void* ptr) {
    if (!enabled_ || !ptr) return;

    std::lock_guard<std::mutex> lock(mutex_);
    freed_pointers_.insert(ptr);
}

void DoubleFreeDetector::checkAndRecordFree(void* ptr) {
    if (!enabled_ || !ptr) return;

    std::lock_guard<std::mutex> lock(mutex_);

    if (freed_pointers_.find(ptr) != freed_pointers_.end()) {
        auto trace = std::stacktrace::current(1, 10);
        std::cerr << "DOUBLE-FREE DETECTED!\n";
        std::cerr << "Pointer: " << ptr << "\n";
        std::cerr << "Stack trace:\n" << trace << "\n";
        throw std::runtime_error("Double-free detected");
    }

    freed_pointers_.insert(ptr);
}

void DoubleFreeDetector::reset() {
    std::lock_guard<std::mutex> lock(mutex_);
    freed_pointers_.clear();
}

void DoubleFreeDetector::setEnabled(bool enabled) {
    std::lock_guard<std::mutex> lock(mutex_);
    enabled_ = enabled;
}

bool DoubleFreeDetector::isEnabled() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return enabled_;
}

DoubleFreeDetectionScope::DoubleFreeDetectionScope(bool enable)
    : previous_state_(DoubleFreeDetector::instance().isEnabled())
{
    DoubleFreeDetector::instance().setEnabled(enable);
}

DoubleFreeDetectionScope::~DoubleFreeDetectionScope() {
    DoubleFreeDetector::instance().setEnabled(previous_state_);
}

} // namespace voltron::utility::memory
