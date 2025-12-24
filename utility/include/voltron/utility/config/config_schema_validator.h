#pragma once

#include <string>
#include <vector>

namespace voltron::utility::config {

/**
 * @brief Validate config against schema
 * 
 * TODO: Implement comprehensive config_schema_validator functionality
 */
class ConfigSchemaValidator {
public:
    static ConfigSchemaValidator& instance();

    /**
     * @brief Initialize config_schema_validator
     */
    void initialize();

    /**
     * @brief Shutdown config_schema_validator
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    ConfigSchemaValidator() = default;
    ~ConfigSchemaValidator() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::config
