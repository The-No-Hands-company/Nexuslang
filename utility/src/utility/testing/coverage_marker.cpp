#include <voltron/utility/testing/coverage_marker.h>
#include <iostream>

namespace voltron::utility::testing {

CoverageMarker& CoverageMarker::instance() {
    static CoverageMarker instance;
    return instance;
}

void CoverageMarker::initialize() {
    enabled_ = true;
    std::cout << "[CoverageMarker] Initialized\n";
}

void CoverageMarker::shutdown() {
    enabled_ = false;
    std::cout << "[CoverageMarker] Shutdown\n";
}

bool CoverageMarker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::testing
