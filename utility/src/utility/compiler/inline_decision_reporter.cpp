#include <voltron/utility/compiler/inline_decision_reporter.h>
#include <iostream>

namespace voltron::utility::compiler {

InlineDecisionReporter& InlineDecisionReporter::instance() {
    static InlineDecisionReporter instance;
    return instance;
}

void InlineDecisionReporter::initialize() {
    enabled_ = true;
    std::cout << "[InlineDecisionReporter] Initialized\n";
}

void InlineDecisionReporter::shutdown() {
    enabled_ = false;
    std::cout << "[InlineDecisionReporter] Shutdown\n";
}

bool InlineDecisionReporter::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::compiler
