#include <voltron/utility/compiler/symbol_visibility_checker.h>
#include <iostream>

namespace voltron::utility::compiler {

SymbolVisibilityChecker& SymbolVisibilityChecker::instance() {
    static SymbolVisibilityChecker instance;
    return instance;
}

void SymbolVisibilityChecker::initialize() {
    enabled_ = true;
    std::cout << "[SymbolVisibilityChecker] Initialized\n";
}

void SymbolVisibilityChecker::shutdown() {
    enabled_ = false;
    std::cout << "[SymbolVisibilityChecker] Shutdown\n";
}

bool SymbolVisibilityChecker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::compiler
