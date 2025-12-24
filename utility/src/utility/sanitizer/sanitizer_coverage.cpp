#include <voltron/utility/sanitizer/sanitizer_coverage.h>
#include <iostream>

namespace voltron::utility::sanitizer {

SanitizerCoverage& SanitizerCoverage::instance() {
    static SanitizerCoverage instance;
    return instance;
}

void SanitizerCoverage::initialize() {
    enabled_ = true;
    std::cout << "[SanitizerCoverage] Initialized\n";
}

void SanitizerCoverage::shutdown() {
    enabled_ = false;
    std::cout << "[SanitizerCoverage] Shutdown\n";
}

bool SanitizerCoverage::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::sanitizer
