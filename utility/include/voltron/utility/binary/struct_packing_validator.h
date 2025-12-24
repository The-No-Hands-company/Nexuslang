#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::binary {

/**
 * @brief Validate structure memory layout
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Binary
 * @version 1.0.0
 */
class StructPackingValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static StructPackingValidator& instance();

    /**
     * @brief Initialize the utility
     * @param config Optional configuration parameters
     */
    void initialize(const std::string& config = "");

    /**
     * @brief Shutdown the utility and cleanup resources
     */
    void shutdown();

    /**
     * @brief Check if the utility is currently enabled
     */
    bool isEnabled() const;

    /**
     * @brief Enable the utility
     */
    void enable();

    /**
     * @brief Disable the utility
     */
    void disable();

    /**
     * @brief Get utility statistics/status
     */
    std::string getStatus() const;

    /**
     * @brief Reset utility state
     */
    void reset();

private:
    StructPackingValidator() = default;
    ~StructPackingValidator() = default;
    
    // Non-copyable, non-movable
    StructPackingValidator(const StructPackingValidator&) = delete;
    StructPackingValidator& operator=(const StructPackingValidator&) = delete;
    StructPackingValidator(StructPackingValidator&&) = delete;
    StructPackingValidator& operator=(StructPackingValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::binary
