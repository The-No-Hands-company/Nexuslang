#include <voltron/utility/audio/audio_buffer_underrun_detector.h>
#include <iostream>

namespace voltron::utility::audio {

AudioBufferUnderrunDetector& AudioBufferUnderrunDetector::instance() {
    static AudioBufferUnderrunDetector instance;
    return instance;
}

void AudioBufferUnderrunDetector::initialize() {
    enabled_ = true;
}

void AudioBufferUnderrunDetector::shutdown() {
    enabled_ = false;
}

bool AudioBufferUnderrunDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::audio
