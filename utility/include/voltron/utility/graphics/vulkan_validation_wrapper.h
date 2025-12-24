#pragma once

#include <string>
#include <vector>

namespace voltron::utility::graphics {

/**
 * @brief Enhanced Vulkan validation
 * 
 * TODO: Implement comprehensive vulkan_validation_wrapper functionality
 */
class VulkanValidationWrapper {
public:
    static VulkanValidationWrapper& instance();

    /**
     * @brief Initialize vulkan_validation_wrapper
     */
    void initialize();

    /**
     * @brief Shutdown vulkan_validation_wrapper
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    VulkanValidationWrapper() = default;
    ~VulkanValidationWrapper() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::graphics
