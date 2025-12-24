#include <voltron/utility/embedded/wcet_analyzer.h>
#include <iostream>

namespace voltron::utility::embedded {

WcetAnalyzer& WcetAnalyzer::instance() {
    static WcetAnalyzer instance;
    return instance;
}

void WcetAnalyzer::initialize() {
    enabled_ = true;
}

void WcetAnalyzer::shutdown() {
    enabled_ = false;
}

bool WcetAnalyzer::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::embedded
