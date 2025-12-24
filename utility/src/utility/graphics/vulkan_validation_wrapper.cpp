#include <voltron/utility/graphics/vulkan_validation_wrapper.h>
#include <iostream>

namespace voltron::utility::graphics {

VulkanValidationWrapper& VulkanValidationWrapper::instance() {
    static VulkanValidationWrapper instance;
    return instance;
}

void VulkanValidationWrapper::initialize() {
    enabled_ = true;
    std::cout << "[VulkanValidationWrapper] Initialized\n";
}

void VulkanValidationWrapper::shutdown() {
    enabled_ = false;
    std::cout << "[VulkanValidationWrapper] Shutdown\n";
}

bool VulkanValidationWrapper::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::graphics
