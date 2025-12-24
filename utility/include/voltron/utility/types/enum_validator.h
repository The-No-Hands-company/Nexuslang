#pragma once

#include <string>
#include <vector>

namespace voltron::utility::types {

/**
 * @brief Validate enum values
 * 
 * TODO: Implement comprehensive enum_validator functionality
 */
class EnumValidator {
public:
    static EnumValidator& instance();

    /**
     * @brief Initialize enum_validator
     */
    void initialize();

    /**
     * @brief Shutdown enum_validator
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    EnumValidator() = default;
    ~EnumValidator() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::types
