#include <voltron/utility/graphics/texture_leak_detector.h>
#include <iostream>

namespace voltron::utility::graphics {

TextureLeakDetector& TextureLeakDetector::instance() {
    static TextureLeakDetector instance;
    return instance;
}

void TextureLeakDetector::initialize() {
    enabled_ = true;
    std::cout << "[TextureLeakDetector] Initialized\n";
}

void TextureLeakDetector::shutdown() {
    enabled_ = false;
    std::cout << "[TextureLeakDetector] Shutdown\n";
}

bool TextureLeakDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::graphics
