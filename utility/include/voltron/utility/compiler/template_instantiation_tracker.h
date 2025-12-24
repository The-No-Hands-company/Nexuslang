#pragma once

#include <string>
#include <vector>

namespace voltron::utility::compiler {

/**
 * @brief Track template instantiations
 * 
 * TODO: Implement comprehensive template_instantiation_tracker functionality
 */
class TemplateInstantiationTracker {
public:
    static TemplateInstantiationTracker& instance();

    /**
     * @brief Initialize template_instantiation_tracker
     */
    void initialize();

    /**
     * @brief Shutdown template_instantiation_tracker
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    TemplateInstantiationTracker() = default;
    ~TemplateInstantiationTracker() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::compiler
