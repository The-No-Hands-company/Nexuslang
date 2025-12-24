#include <voltron/utility/timing/jitter_analyzer.h>
#include <iostream>

namespace voltron::utility::timing {

JitterAnalyzer& JitterAnalyzer::instance() {
    static JitterAnalyzer instance;
    return instance;
}

void JitterAnalyzer::initialize() {
    enabled_ = true;
    std::cout << "[JitterAnalyzer] Initialized\n";
}

void JitterAnalyzer::shutdown() {
    enabled_ = false;
    std::cout << "[JitterAnalyzer] Shutdown\n";
}

bool JitterAnalyzer::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::timing
