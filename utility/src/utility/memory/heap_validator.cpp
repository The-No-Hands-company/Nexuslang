#include <voltron/utility/memory/heap_validator.h>
#include <iostream>
#include <cstring>

namespace voltron::utility::memory {

HeapValidator& HeapValidator::instance() {
    static HeapValidator instance;
    return instance;
}

HeapValidator::~HeapValidator() {
    disablePeriodicValidation();
}

HeapValidator::ValidationResult HeapValidator::validate() {
    ValidationResult result;
    
    for (const auto& block : registered_blocks_) {
        auto block_result = validateBlock(block);
        result.is_valid &= block_result.is_valid;
        result.errors.insert(result.errors.end(),
                            block_result.errors.begin(),
                            block_result.errors.end());
        result.allocations_checked += block_result.allocations_checked;
        result.corruptions_found += block_result.corruptions_found;
    }
    
    if (callback_ && !result.is_valid) {
        callback_(result);
    }
    
    return result;
}

void HeapValidator::enablePeriodicValidation(int interval_ms) {
    periodic_enabled_ = true;
    // Implementation would spawn a thread for periodic validation
    // Omitted for brevity - would use std::thread with sleep loop
    (void)interval_ms;
}

void HeapValidator::disablePeriodicValidation() {
    periodic_enabled_ = false;
    // Stop validation thread
}

void HeapValidator::setValidationCallback(ValidationCallback callback) {
    callback_ = std::move(callback);
}

void HeapValidator::registerHeapBlock(void* start, size_t size, const std::string& name) {
    registered_blocks_.push_back({start, size, name});
}

void HeapValidator::unregisterHeapBlock(void* start) {
    registered_blocks_.erase(
        std::remove_if(registered_blocks_.begin(), registered_blocks_.end(),
                      [start](const HeapBlock& block) { return block.start == start; }),
        registered_blocks_.end());
}

HeapValidator::ValidationResult HeapValidator::validateBlock(const HeapBlock& block) {
    ValidationResult result;
    result.allocations_checked = 1;
    
    // Perform basic validity checks
    if (!block.start) {
        result.is_valid = false;
        result.errors.push_back("Null heap block: " + block.name);
        result.corruptions_found++;
        return result;
    }
    
    // Check for obvious corruption (all zeros or all 0xFF)
    const uint8_t* data = static_cast<const uint8_t*>(block.start);
    bool all_zeros = true;
    bool all_ff = true;
    
    for (size_t i = 0; i < std::min(block.size, size_t(256)); ++i) {
        if (data[i] != 0) all_zeros = false;
        if (data[i] != 0xFF) all_ff = false;
    }
    
    if (all_zeros || all_ff) {
        result.errors.push_back("Suspicious memory pattern in block: " + block.name);
        // Not necessarily invalid, just suspicious
    }
    
    return result;
}

} // namespace voltron::utility::memory
