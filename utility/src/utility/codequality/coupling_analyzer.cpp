#include <voltron/utility/codequality/coupling_analyzer.h>
#include <iostream>

namespace voltron::utility::codequality {

CouplingAnalyzer& CouplingAnalyzer::instance() {
    static CouplingAnalyzer instance;
    return instance;
}

void CouplingAnalyzer::initialize() {
    enabled_ = true;
}

void CouplingAnalyzer::shutdown() {
    enabled_ = false;
}

bool CouplingAnalyzer::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::codequality
