#pragma once

#include <string>
#include <vector>

namespace voltron::utility::graphics {

/**
 * @brief DirectX 12 debug utilities
 * 
 * TODO: Implement comprehensive dx12_debug_layer_wrapper functionality
 */
class Dx12DebugLayerWrapper {
public:
    static Dx12DebugLayerWrapper& instance();

    /**
     * @brief Initialize dx12_debug_layer_wrapper
     */
    void initialize();

    /**
     * @brief Shutdown dx12_debug_layer_wrapper
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    Dx12DebugLayerWrapper() = default;
    ~Dx12DebugLayerWrapper() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::graphics
