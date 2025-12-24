#pragma once

#include <string>
#include <vector>

namespace voltron::utility::graphics {

/**
 * @brief Track GPU textures
 * 
 * TODO: Implement comprehensive texture_leak_detector functionality
 */
class TextureLeakDetector {
public:
    static TextureLeakDetector& instance();

    /**
     * @brief Initialize texture_leak_detector
     */
    void initialize();

    /**
     * @brief Shutdown texture_leak_detector
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    TextureLeakDetector() = default;
    ~TextureLeakDetector() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::graphics
