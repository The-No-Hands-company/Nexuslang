#pragma once

#include <string>
#include <vector>

namespace voltron::utility::audio {

/**
 * @brief Validate audio sample rates
 */
class SampleRateValidator {
public:
    static SampleRateValidator& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    SampleRateValidator() = default;
    ~SampleRateValidator() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::audio
