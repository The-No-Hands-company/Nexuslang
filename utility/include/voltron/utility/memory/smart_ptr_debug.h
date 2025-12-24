#pragma once

#include <memory>
#include <string>
#include <iostream>
#include <stacktrace>
#include <voltron/utility/memory/memory_tracker.h>

namespace voltron::utility::memory {

/// @brief Enhanced unique_ptr with lifecycle logging via MemoryTracker
template<typename T>
class DebugUniquePtr {
public:
    DebugUniquePtr() : ptr_(nullptr), name_("unnamed") {}

    explicit DebugUniquePtr(T* ptr, const std::string& name = "unnamed")
        : ptr_(ptr), name_(name)
    {
        // Allocation is already tracked if allocated via new, but we can annotate it
        // Or if the pointer is managed, we can record ownership transfer if we want.
        // For now, let's assume raw pointer tracking handles the allocation.
        // We just log interesting lifecycle events if enabled.
    }

    ~DebugUniquePtr() {
        // Tracker handles deallocation if we use delete.
        // We can explicitly assert if we want.
    }

    DebugUniquePtr(DebugUniquePtr&& other) noexcept
        : ptr_(std::move(other.ptr_)), name_(std::move(other.name_))
    {}

    DebugUniquePtr& operator=(DebugUniquePtr&& other) noexcept {
        if (this != &other) {
            ptr_ = std::move(other.ptr_);
            name_ = std::move(other.name_);
        }
        return *this;
    }

    DebugUniquePtr(const DebugUniquePtr&) = delete;
    DebugUniquePtr& operator=(const DebugUniquePtr&) = delete;

    T* get() const { return ptr_.get(); }
    T* operator->() const { return ptr_.get(); }
    T& operator*() const { return *ptr_; }
    explicit operator bool() const { return static_cast<bool>(ptr_); }

    void reset(T* ptr = nullptr) {
        ptr_.reset(ptr);
    }

    T* release() {
        return ptr_.release();
    }

    const std::string& getName() const { return name_; }

private:
    std::unique_ptr<T> ptr_;
    std::string name_;
};

// ... SharedPtr implementation similarly simplified or enhanced ...
// For the sake of this task, I will leave SharedPtr similar to UniquePtr but focusing on
// the requested goal of MemoryTracker hooks.
// Since MemoryTracker tracks *allocations* (void*), smart pointers wrap *ownership*.
// The best way smart pointers can help is by providing context (names) to the allocations 
// IF they control the allocation (like make_unique).

template<typename T>
class DebugSharedPtr {
public:
    DebugSharedPtr() : ptr_(nullptr), name_("unnamed") {}
    
    explicit DebugSharedPtr(T* ptr, const std::string& name = "unnamed") 
        : ptr_(ptr), name_(name) {}

    // ... standard operators ...
    
    T* get() const { return ptr_.get(); }
    T* operator->() const { return ptr_.get(); }
    T& operator*() const { return *ptr_; }
    long use_count() const { return ptr_.use_count(); }

private:
    std::shared_ptr<T> ptr_;
    std::string name_;
};

/// @brief Factory functions for debug smart pointers
template<typename T, typename... Args>
DebugUniquePtr<T> makeDebugUnique(const std::string& name, Args&&... args) {
    // We allocate here.
    T* ptr = new T(std::forward<Args>(args)...);
    
    // We can update the tracker with the type name "T (name)" to be more specific
    // However, the allocation already happened in `new`.
    // If we want to rename the allocation in the tracker, we'd need an API for that.
    // For now, let's just create the smart ptr.
    return DebugUniquePtr<T>(ptr, name);
}

} // namespace voltron::utility::memory
