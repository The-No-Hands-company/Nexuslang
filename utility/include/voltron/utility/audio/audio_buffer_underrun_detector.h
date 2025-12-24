#pragma once

#include <string>
#include <vector>

namespace voltron::utility::audio {

/**
 * @brief Detect audio glitches
 */
class AudioBufferUnderrunDetector {
public:
    static AudioBufferUnderrunDetector& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    AudioBufferUnderrunDetector() = default;
    ~AudioBufferUnderrunDetector() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::audio
