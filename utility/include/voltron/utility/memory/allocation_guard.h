#pragma once

#include <string>
#include <chrono>
#include <iostream>
#include <stdexcept>
#include <voltron/utility/memory/memory_tracker.h>

namespace voltron::utility::memory {

/// @brief RAII guard for tracking allocations within a scope
class AllocationGuard {
public:
    explicit AllocationGuard(const std::string& scope_name, bool fail_on_allocation = false)
        : scope_name_(scope_name)
        , fail_on_allocation_(fail_on_allocation)
        , start_time_(std::chrono::steady_clock::now())
        , start_stats_(MemoryTracker::instance().getStats())
    {
    }

    ~AllocationGuard() {
        if (std::uncaught_exceptions() > 0) return; // Don't crash if already unwinding

        auto end_stats = MemoryTracker::instance().getStats();
        size_t new_allocs = end_stats.total_allocations - start_stats_.total_allocations;
        
        // Duration logging is optional, maybe too noisy
        // auto end_time = std::chrono::steady_clock::now();
        
        if (new_allocs > 0) {
            if (fail_on_allocation_) {
                std::cerr << "[AllocationGuard] VIOLATION in '" << scope_name_ 
                          << "': " << new_allocs << " allocation(s) detected!\n";
                // We should ideally throw or abort, but throwing in destructor is bad.
                // Since this is a guard specifically for this purpose, aborting might be desired 
                // or we log loudly.
                std::cerr << "Aborting due to forbidden allocation.\n";
                std::abort();
            } else {
                // Just log
                // std::cerr << "[AllocationGuard] Scope '" << scope_name_ << "': " << new_allocs << " allocations.\n";
            }
        }
    }

    AllocationGuard(const AllocationGuard&) = delete;
    AllocationGuard& operator=(const AllocationGuard&) = delete;

private:
    std::string scope_name_;
    bool fail_on_allocation_;
    std::chrono::steady_clock::time_point start_time_;
    MemoryStats start_stats_;
};

#define VOLTRON_ALLOCATION_GUARD(name) \
    voltron::utility::memory::AllocationGuard _alloc_guard_##__LINE__(name)

#define VOLTRON_NO_ALLOCATIONS(name) \
    voltron::utility::memory::AllocationGuard _alloc_guard_##__LINE__(name, true)

} // namespace voltron::utility::memory
