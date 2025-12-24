#include <voltron/utility/audio/audio_latency_tracker.h>
#include <iostream>

namespace voltron::utility::audio {

AudioLatencyTracker& AudioLatencyTracker::instance() {
    static AudioLatencyTracker instance;
    return instance;
}

void AudioLatencyTracker::initialize() {
    enabled_ = true;
}

void AudioLatencyTracker::shutdown() {
    enabled_ = false;
}

bool AudioLatencyTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::audio
