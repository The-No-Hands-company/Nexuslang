#include "voltron/utility/memory/memory_tracker.h"
#include <iostream>
#include <iomanip>
#include <sstream>

namespace voltron::utility::memory {

AllocationStackTrace::AllocationStackTrace(void* addr, size_t sz, const char* type)
// NOTE: Stack trace capture is now done in recordAllocation based on config
    : size(sz)
    , address(addr)
    , type_name(type ? type : "unknown")
{}

void MemoryStats::recordAllocation(size_t size) {
    total_allocations++;
    current_allocations++;
    total_bytes_allocated += size;
    current_bytes += size;

    if (current_allocations > peak_allocations) {
        peak_allocations = current_allocations;
    }
    if (current_bytes > peak_bytes) {
        peak_bytes = current_bytes;
    }
}

void MemoryStats::recordDeallocation(size_t size) {
    total_deallocations++;
    if (current_allocations > 0) {
        current_allocations--;
    }
    total_bytes_deallocated += size;
    if (current_bytes >= size) {
        current_bytes -= size;
    }
}

MemoryTracker& MemoryTracker::instance() {
    static MemoryTracker tracker;
    return tracker;
}

MemoryTracker::~MemoryTracker() {
    // If tracking is still permitted, we might warn about leaks.
    // However, static destruction order is tricky.
    // We try to report if we are confident it's a leak.
    if (!allocations_.empty() && config_.track_allocations) {
        // Use a safe way to print, avoiding allocations if possible
        // But std::stacktrace printing might allocate.
        std::cerr << "WARNING: Memory leaks detected at shutdown!\n";
         // We can't easily lock mutex here if it's already destroyed or in undefined state
         // But since we are in destructor, we assume single threaded access to *this
        
        // Caution: printReport locks.
        // We will try to print.
        try {
            printReport(std::cerr);
        } catch (...) {
            std::cerr << "[MemoryTracker] Failed to print leak report during destruction.\n";
        }
    }
}

void MemoryTracker::configure(const Config& config) {
    std::lock_guard<std::mutex> lock(mutex_);
    config_ = config;
}

MemoryTracker::Config MemoryTracker::getConfig() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return config_;
}

void MemoryTracker::recordAllocation(void* ptr, size_t size, const char* type_name) {
    // Avoid mutex if tracking is disabled globally (optimization)
    // But we need to check config safely.
    // We can assume unchecked read for bool is okayish for loose consistency,
    // but better be correct.
    
    // Optimistic check
    // if (!config_.track_allocations) return; 

    if (!ptr) return;

    std::lock_guard<std::mutex> lock(mutex_);
    if (!config_.track_allocations) return;

    AllocationStackTrace info(ptr, size, type_name);
    
    if (config_.capture_stack_traces) {
        // stacktrace::current is slow
        try {
            info.trace = std::stacktrace::current(config_.stack_trace_skip, config_.stack_trace_depth);
        } catch (...) {
            // Stack trace capture failed (e.g. bad alloc), ignore
        }
    }

    allocations_.emplace(ptr, std::move(info));
    stats_.recordAllocation(size);
}

void MemoryTracker::recordDeallocation(void* ptr) {
    if (!ptr) return;

    std::lock_guard<std::mutex> lock(mutex_);
    if (!config_.track_allocations) return;

    auto it = allocations_.find(ptr);
    if (it != allocations_.end()) {
        stats_.recordDeallocation(it->second.size);
        allocations_.erase(it);
    } else {
        // Attempt to free unknown pointer?
        // Could be allocated before tracker started or from untracked source.
    }
}

MemoryStats MemoryTracker::getStats() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return stats_;
}

std::vector<AllocationStackTrace> MemoryTracker::detectLeaks() const {
    std::lock_guard<std::mutex> lock(mutex_);
    std::vector<AllocationStackTrace> leaks;
    leaks.reserve(allocations_.size());
    for (const auto& [ptr, trace] : allocations_) {
        leaks.push_back(trace);
    }
    return leaks;
}

void MemoryTracker::printReport(std::ostream& os) const {
    std::lock_guard<std::mutex> lock(mutex_);

    os << "\n=== Memory Tracker Report ===\n";
    os << "Total allocations:     " << stats_.total_allocations << "\n";
    os << "Total deallocations:   " << stats_.total_deallocations << "\n";
    os << "Current allocations:   " << stats_.current_allocations << "\n";
    os << "Peak allocations:      " << stats_.peak_allocations << "\n";
    os << "Total bytes allocated: " << stats_.total_bytes_allocated << "\n";
    os << "Total bytes freed:     " << stats_.total_bytes_deallocated << "\n";
    os << "Current bytes:         " << stats_.current_bytes << "\n";
    os << "Peak bytes:            " << stats_.peak_bytes << "\n";

    if (!allocations_.empty()) {
        os << "\n=== Active Allocations (Potential Leaks) ===\n";
        for (const auto& [ptr, trace] : allocations_) {
            os << "\nAddress: " << ptr << " | Size: " << trace.size
               << " bytes | Type: " << trace.type_name << "\n";
            if (!trace.trace.empty()) {
                os << "Stack trace:\n" << trace.trace << "\n";
            } else {
                 os << "Stack trace: [Disabled or not captured]\n";
            }
        }
    }
    os << "=============================\n\n";
}

void MemoryTracker::reset() {
    std::lock_guard<std::mutex> lock(mutex_);
    allocations_.clear();
    stats_ = MemoryStats{};
}

void MemoryTracker::setEnabled(bool enabled) {
    std::lock_guard<std::mutex> lock(mutex_);
    config_.track_allocations = enabled;
}

bool MemoryTracker::isEnabled() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return config_.track_allocations;
}

MemoryTrackingScope::MemoryTrackingScope(bool enable)
    : previous_state_(MemoryTracker::instance().isEnabled())
{
    MemoryTracker::instance().setEnabled(enable);
}

MemoryTrackingScope::~MemoryTrackingScope() {
    MemoryTracker::instance().setEnabled(previous_state_);
}

} // namespace voltron::utility::memory
