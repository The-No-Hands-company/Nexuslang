#include <voltron/utility/memory/memory_pool_debug.h>
#include <iomanip>
#include <iostream>
#include <cstring>

namespace voltron::utility::memory {

MemoryPoolDebug::MemoryPoolDebug(const PoolConfig& config)
    : config_(config),
      pool_memory_(std::make_unique<uint8_t[]>(config.pool_size)) {
    std::memset(pool_memory_.get(), 0, config.pool_size);
}

MemoryPoolDebug::~MemoryPoolDebug() {
    auto leaks = detectLeaks();
    if (!leaks.empty() && config_.enable_leak_detection) {
        std::cerr << "[MemoryPoolDebug] Pool '" << config_.pool_name 
                  << "' destroyed with " << leaks.size() << " leaks!\n";
        printReport(std::cerr);
    }
}

void* MemoryPoolDebug::allocate(size_t size, size_t alignment,
                                 const std::source_location& loc) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    // Calculate total size with canaries if enabled
    size_t total_size = size;
    if (config_.enable_canaries) {
        total_size += sizeof(uint32_t) * 2;  // Front and back canaries
    }
    
    // Align offset
    size_t aligned_offset = (current_offset_ + alignment - 1) & ~(alignment - 1);
    
    // Check if we have space
    if (aligned_offset + total_size > config_.pool_size) {
        stats_.failed_allocations++;
        return nullptr;
    }
    
    void* ptr = pool_memory_.get() + aligned_offset;
    
    // Place canaries if enabled
    if (config_.enable_canaries) {
        ptr = placeCanaries(ptr, size);
    }
    
    // Track allocation
    AllocationInfo info;
    info.ptr = ptr;
    info.size = size;
    info.location = loc;
    allocations_[ptr] = info;
    
    // Update statistics
    stats_.total_allocated += size;
    stats_.current_allocations++;
    size_t current_usage = aligned_offset + total_size;
    if (current_usage > stats_.peak_usage) {
        stats_.peak_usage = current_usage;
    }
    
    current_offset_ = aligned_offset + total_size;
    
    return ptr;
}

void MemoryPoolDebug::deallocate(void* ptr, const std::source_location& loc) {
    if (!ptr) return;
    
    std::lock_guard<std::mutex> lock(mutex_);
    
    auto it = allocations_.find(ptr);
    if (it == allocations_.end()) {
        std::cerr << "[MemoryPoolDebug] Double-free or invalid pointer detected!\n"
                  << "  Location: " << loc.file_name() << ":" << loc.line() << "\n";
        return;
    }
    
    if (it->second.is_freed) {
        std::cerr << "[MemoryPoolDebug] Double-free detected!\n"
                  << "  Allocated: " << it->second.location.file_name() << ":" 
                  << it->second.location.line() << "\n"
                  << "  Freed at: " << loc.file_name() << ":" << loc.line() << "\n";
        return;
    }
    
    // Check canaries
    if (config_.enable_canaries && !checkCanaries(ptr)) {
        std::cerr << "[MemoryPoolDebug] Buffer overflow detected!\n"
                  << "  Allocated: " << it->second.location.file_name() << ":" 
                  << it->second.location.line() << "\n";
    }
    
    // Poison memory if enabled
    if (config_.poison_freed_memory) {
        poisonMemory(ptr, it->second.size);
    }
    
    it->second.is_freed = true;
    stats_.total_freed += it->second.size;
    stats_.current_allocations--;
}

std::vector<MemoryPoolDebug::AllocationInfo> MemoryPoolDebug::detectLeaks() const {
    std::lock_guard<std::mutex> lock(mutex_);
    
    std::vector<AllocationInfo> leaks;
    for (const auto& [ptr, info] : allocations_) {
        if (!info.is_freed) {
            leaks.push_back(info);
        }
    }
    return leaks;
}

bool MemoryPoolDebug::validateIntegrity() const {
    if (!config_.enable_canaries) return true;
    
    std::lock_guard<std::mutex> lock(mutex_);
    
    for (const auto& [ptr, info] : allocations_) {
        if (!info.is_freed && !checkCanaries(ptr)) {
            return false;
        }
    }
    return true;
}

void MemoryPoolDebug::reset() {
    std::lock_guard<std::mutex> lock(mutex_);
    allocations_.clear();
    current_offset_ = 0;
    stats_ = Statistics{};
}

MemoryPoolDebug::Statistics MemoryPoolDebug::getStatistics() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return stats_;
}

void MemoryPoolDebug::printReport(std::ostream& os) const {
    std::lock_guard<std::mutex> lock(mutex_);
    
    os << "=== Memory Pool Debug Report: " << config_.pool_name << " ===\n";
    os << "Pool Size: " << config_.pool_size << " bytes\n";
    os << "Total Allocated: " << stats_.total_allocated << " bytes\n";
    os << "Total Freed: " << stats_.total_freed << " bytes\n";
    os << "Current Allocations: " << stats_.current_allocations << "\n";
    os << "Peak Usage: " << stats_.peak_usage << " bytes\n";
    os << "Failed Allocations: " << stats_.failed_allocations << "\n\n";
    
    auto leaks = detectLeaks();
    if (!leaks.empty()) {
        os << "Active Allocations (Leaks):\n";
        for (const auto& leak : leaks) {
            os << "  " << leak.ptr << " - " << leak.size << " bytes\n"
               << "    Allocated at: " << leak.location.file_name() << ":" 
               << leak.location.line() << "\n";
        }
    }
    os << "==========================================\n";
}

void* MemoryPoolDebug::placeCanaries(void* ptr, size_t size) {
    uint32_t* front = static_cast<uint32_t*>(ptr);
    *front = CANARY_VALUE;
    
    uint8_t* user_ptr = reinterpret_cast<uint8_t*>(ptr) + sizeof(uint32_t);
    uint32_t* back = reinterpret_cast<uint32_t*>(user_ptr + size);
    *back = CANARY_VALUE;
    
    return user_ptr;
}

bool MemoryPoolDebug::checkCanaries(void* user_ptr) const {
    uint8_t* base = reinterpret_cast<uint8_t*>(user_ptr) - sizeof(uint32_t);
    uint32_t* front = reinterpret_cast<uint32_t*>(base);
    
    auto it = allocations_.find(user_ptr);
    if (it == allocations_.end()) return false;
    
    uint32_t* back = reinterpret_cast<uint32_t*>(
        reinterpret_cast<uint8_t*>(user_ptr) + it->second.size);
    
    return (*front == CANARY_VALUE) && (*back == CANARY_VALUE);
}

void MemoryPoolDebug::poisonMemory(void* ptr, size_t size) {
    std::memset(ptr, config_.poison_byte, size);
}

} // namespace voltron::utility::memory
