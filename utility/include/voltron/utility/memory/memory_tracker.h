#pragma once

#include <cstddef>
#include <string>
#include <vector>
#include <mutex>
#include <unordered_map>
#include <stacktrace>
#include <iostream>

namespace voltron::utility::memory {

struct AllocationStackTrace {
    std::stacktrace trace;
    size_t size;
    void* address;
    std::string type_name;

    AllocationStackTrace(void* addr, size_t sz, const char* type = "unknown");
};

struct MemoryStats {
    size_t total_allocations = 0;
    size_t total_deallocations = 0;
    size_t current_allocations = 0;
    size_t peak_allocations = 0;
    size_t total_bytes_allocated = 0;
    size_t total_bytes_deallocated = 0;
    size_t current_bytes = 0;
    size_t peak_bytes = 0;

    void recordAllocation(size_t size);
    void recordDeallocation(size_t size);
    
    // Add comparison operators for AllocationGuard
    bool operator==(const MemoryStats& other) const = default;
};

class MemoryTracker {
public:
    static MemoryTracker& instance();

    struct Config {
        bool capture_stack_traces = true;
        bool track_allocations = true;
        size_t stack_trace_depth = 10;
        size_t stack_trace_skip = 1;
    };

    void configure(const Config& config);
    Config getConfig() const;

    void recordAllocation(void* ptr, size_t size, const char* type_name = "unknown");
    void recordDeallocation(void* ptr);

    MemoryStats getStats() const;
    std::vector<AllocationStackTrace> detectLeaks() const;
    void printReport(std::ostream& os) const;
    void reset();

    // Direct enable/disable (updates config.track_allocations)
    void setEnabled(bool enabled);
    bool isEnabled() const;

private:
    MemoryTracker() = default;
    ~MemoryTracker();

    MemoryTracker(const MemoryTracker&) = delete;
    MemoryTracker& operator=(const MemoryTracker&) = delete;

    mutable std::mutex mutex_;
    std::unordered_map<void*, AllocationStackTrace> allocations_;
    MemoryStats stats_;
    Config config_;
};

class MemoryTrackingScope {
public:
    explicit MemoryTrackingScope(bool enable);
    ~MemoryTrackingScope();

private:
    bool previous_state_;
};

} // namespace voltron::utility::memory
