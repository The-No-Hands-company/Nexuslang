#include <voltron/utility/embedded/stack_usage_analyzer.h>
#include <iostream>

namespace voltron::utility::embedded {

StackUsageAnalyzer& StackUsageAnalyzer::instance() {
    static StackUsageAnalyzer instance;
    return instance;
}

void StackUsageAnalyzer::initialize() {
    enabled_ = true;
}

void StackUsageAnalyzer::shutdown() {
    enabled_ = false;
}

bool StackUsageAnalyzer::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::embedded
