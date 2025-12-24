#include <voltron/utility/audio/audio_callback_profiler.h>
#include <iostream>

namespace voltron::utility::audio {

AudioCallbackProfiler& AudioCallbackProfiler::instance() {
    static AudioCallbackProfiler instance;
    return instance;
}

void AudioCallbackProfiler::initialize() {
    enabled_ = true;
}

void AudioCallbackProfiler::shutdown() {
    enabled_ = false;
}

bool AudioCallbackProfiler::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::audio
