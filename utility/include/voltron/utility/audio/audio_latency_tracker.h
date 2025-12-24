#pragma once

#include <string>
#include <vector>

namespace voltron::utility::audio {

/**
 * @brief Monitor audio pipeline latency
 */
class AudioLatencyTracker {
public:
    static AudioLatencyTracker& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    AudioLatencyTracker() = default;
    ~AudioLatencyTracker() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::audio
