#include <voltron/utility/algorithmic/compression_ratio_tracker.h>
#include <iostream>

namespace voltron::utility::algorithmic {

CompressionRatioTracker& CompressionRatioTracker::instance() {
    static CompressionRatioTracker instance;
    return instance;
}

void CompressionRatioTracker::initialize() {
    enabled_ = true;
}

void CompressionRatioTracker::shutdown() {
    enabled_ = false;
}

bool CompressionRatioTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::algorithmic
