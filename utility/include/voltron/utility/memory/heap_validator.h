#pragma once

#include <cstddef>
#include <functional>
#include <string>
#include <vector>

namespace voltron::utility::memory {

/**
 * @brief Periodic heap consistency checker
 * 
 * Validates heap integrity by checking:
 * - Allocation metadata consistency
 * - Free list integrity
 * - Canary values
 * - Reference counts
 */
class HeapValidator {
public:
    struct ValidationResult {
        bool is_valid = true;
        std::vector<std::string> errors;
        size_t allocations_checked = 0;
        size_t corruptions_found = 0;
    };

    using ValidationCallback = std::function<void(const ValidationResult&)>;

    static HeapValidator& instance();

    /**
     * @brief Perform full heap validation
     */
    ValidationResult validate();

    /**
     * @brief Enable automatic periodic validation
     */
    void enablePeriodicValidation(int interval_ms = 5000);

    /**
     * @brief Disable automatic validation
     */
    void disablePeriodicValidation();

    /**
     * @brief Set callback for validation failures
     */
    void setValidationCallback(ValidationCallback callback);

    /**
     * @brief Register custom heap block for validation
     */
    void registerHeapBlock(void* start, size_t size, const std::string& name);

    /**
     * @brief Unregister heap block
     */
    void unregisterHeapBlock(void* start);

private:
    HeapValidator() = default;
    ~HeapValidator();

    struct HeapBlock {
        void* start;
        size_t size;
        std::string name;
    };

    std::vector<HeapBlock> registered_blocks_;
    ValidationCallback callback_;
    bool periodic_enabled_ = false;
    
    ValidationResult validateBlock(const HeapBlock& block);
};

} // namespace voltron::utility::memory
