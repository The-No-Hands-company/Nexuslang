#include <voltron/utility/graphics/dx12_debug_layer_wrapper.h>
#include <iostream>

namespace voltron::utility::graphics {

Dx12DebugLayerWrapper& Dx12DebugLayerWrapper::instance() {
    static Dx12DebugLayerWrapper instance;
    return instance;
}

void Dx12DebugLayerWrapper::initialize() {
    enabled_ = true;
    std::cout << "[Dx12DebugLayerWrapper] Initialized\n";
}

void Dx12DebugLayerWrapper::shutdown() {
    enabled_ = false;
    std::cout << "[Dx12DebugLayerWrapper] Shutdown\n";
}

bool Dx12DebugLayerWrapper::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::graphics
