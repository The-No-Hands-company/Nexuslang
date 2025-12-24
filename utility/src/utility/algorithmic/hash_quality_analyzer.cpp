#include <voltron/utility/algorithmic/hash_quality_analyzer.h>
#include <iostream>

namespace voltron::utility::algorithmic {

HashQualityAnalyzer& HashQualityAnalyzer::instance() {
    static HashQualityAnalyzer instance;
    return instance;
}

void HashQualityAnalyzer::initialize() {
    enabled_ = true;
}

void HashQualityAnalyzer::shutdown() {
    enabled_ = false;
}

bool HashQualityAnalyzer::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::algorithmic
