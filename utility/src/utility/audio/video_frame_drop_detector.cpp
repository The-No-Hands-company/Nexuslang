#include <voltron/utility/audio/video_frame_drop_detector.h>
#include <iostream>

namespace voltron::utility::audio {

VideoFrameDropDetector& VideoFrameDropDetector::instance() {
    static VideoFrameDropDetector instance;
    return instance;
}

void VideoFrameDropDetector::initialize() {
    enabled_ = true;
}

void VideoFrameDropDetector::shutdown() {
    enabled_ = false;
}

bool VideoFrameDropDetector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::audio
