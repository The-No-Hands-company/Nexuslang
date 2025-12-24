#pragma once

#include <string>
#include <vector>

namespace voltron::utility::types {

/**
 * @brief Check bit manipulation correctness
 * 
 * TODO: Implement comprehensive bit_field_validator functionality
 */
class BitFieldValidator {
public:
    static BitFieldValidator& instance();

    /**
     * @brief Initialize bit_field_validator
     */
    void initialize();

    /**
     * @brief Shutdown bit_field_validator
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    BitFieldValidator() = default;
    ~BitFieldValidator() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::types
