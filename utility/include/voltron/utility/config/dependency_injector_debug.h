#pragma once

#include <string>
#include <vector>

namespace voltron::utility::config {

/**
 * @brief DI container diagnostics
 * 
 * TODO: Implement comprehensive dependency_injector_debug functionality
 */
class DependencyInjectorDebug {
public:
    static DependencyInjectorDebug& instance();

    /**
     * @brief Initialize dependency_injector_debug
     */
    void initialize();

    /**
     * @brief Shutdown dependency_injector_debug
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    DependencyInjectorDebug() = default;
    ~DependencyInjectorDebug() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::config
