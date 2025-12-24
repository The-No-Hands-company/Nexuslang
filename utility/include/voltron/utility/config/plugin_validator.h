#pragma once

#include <string>
#include <vector>

namespace voltron::utility::config {

/**
 * @brief Validate dynamically loaded plugins
 * 
 * TODO: Implement comprehensive plugin_validator functionality
 */
class PluginValidator {
public:
    static PluginValidator& instance();

    /**
     * @brief Initialize plugin_validator
     */
    void initialize();

    /**
     * @brief Shutdown plugin_validator
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    PluginValidator() = default;
    ~PluginValidator() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::config
