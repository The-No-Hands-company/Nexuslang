#pragma once

#include <string>
#include <vector>

namespace voltron::utility::graphics {

/**
 * @brief Validate framebuffer completeness
 * 
 * TODO: Implement comprehensive framebuffer_validator functionality
 */
class FramebufferValidator {
public:
    static FramebufferValidator& instance();

    /**
     * @brief Initialize framebuffer_validator
     */
    void initialize();

    /**
     * @brief Shutdown framebuffer_validator
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    FramebufferValidator() = default;
    ~FramebufferValidator() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::graphics
