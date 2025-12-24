#pragma once

#include <string>
#include <vector>

namespace voltron::utility::compiler {

/**
 * @brief Inspect virtual tables
 * 
 * TODO: Implement comprehensive vtable_inspector functionality
 */
class VtableInspector {
public:
    static VtableInspector& instance();

    /**
     * @brief Initialize vtable_inspector
     */
    void initialize();

    /**
     * @brief Shutdown vtable_inspector
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    VtableInspector() = default;
    ~VtableInspector() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::compiler
