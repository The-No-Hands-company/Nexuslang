#include <voltron/utility/audio/sample_rate_validator.h>
#include <iostream>

namespace voltron::utility::audio {

SampleRateValidator& SampleRateValidator::instance() {
    static SampleRateValidator instance;
    return instance;
}

void SampleRateValidator::initialize() {
    enabled_ = true;
}

void SampleRateValidator::shutdown() {
    enabled_ = false;
}

bool SampleRateValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::audio
