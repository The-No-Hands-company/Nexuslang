#pragma once

#include <string>
#include <vector>

namespace voltron::utility::reflection {

/**
 * @brief Inspect object properties
 * 
 * TODO: Implement comprehensive property_inspector functionality
 */
class PropertyInspector {
public:
    static PropertyInspector& instance();

    /**
     * @brief Initialize property_inspector
     */
    void initialize();

    /**
     * @brief Shutdown property_inspector
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    PropertyInspector() = default;
    ~PropertyInspector() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::reflection
