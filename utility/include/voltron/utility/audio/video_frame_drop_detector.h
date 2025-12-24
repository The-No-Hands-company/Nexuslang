#pragma once

#include <string>
#include <vector>

namespace voltron::utility::audio {

/**
 * @brief Detect dropped frames
 */
class VideoFrameDropDetector {
public:
    static VideoFrameDropDetector& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    VideoFrameDropDetector() = default;
    ~VideoFrameDropDetector() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::audio
