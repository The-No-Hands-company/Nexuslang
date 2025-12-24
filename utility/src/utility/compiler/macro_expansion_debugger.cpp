#include <voltron/utility/compiler/macro_expansion_debugger.h>
#include <iostream>

namespace voltron::utility::compiler {

MacroExpansionDebugger& MacroExpansionDebugger::instance() {
    static MacroExpansionDebugger instance;
    return instance;
}

void MacroExpansionDebugger::initialize() {
    enabled_ = true;
    std::cout << "[MacroExpansionDebugger] Initialized\n";
}

void MacroExpansionDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[MacroExpansionDebugger] Shutdown\n";
}

bool MacroExpansionDebugger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::compiler
