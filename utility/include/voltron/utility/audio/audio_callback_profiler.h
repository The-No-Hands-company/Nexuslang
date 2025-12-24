#pragma once

#include <string>
#include <vector>

namespace voltron::utility::audio {

/**
 * @brief Profile real-time audio callbacks
 */
class AudioCallbackProfiler {
public:
    static AudioCallbackProfiler& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    AudioCallbackProfiler() = default;
    ~AudioCallbackProfiler() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::audio
