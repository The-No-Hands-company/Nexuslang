#include <voltron/utility/algorithmic/random_quality_tester.h>
#include <iostream>

namespace voltron::utility::algorithmic {

RandomQualityTester& RandomQualityTester::instance() {
    static RandomQualityTester instance;
    return instance;
}

void RandomQualityTester::initialize() {
    enabled_ = true;
}

void RandomQualityTester::shutdown() {
    enabled_ = false;
}

bool RandomQualityTester::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::algorithmic
