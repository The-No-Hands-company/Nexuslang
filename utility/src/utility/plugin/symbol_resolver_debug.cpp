#include <voltron/utility/plugin/symbol_resolver_debug.h>
#include <iostream>

namespace voltron::utility::plugin {

SymbolResolverDebug& SymbolResolverDebug::instance() {
    static SymbolResolverDebug instance;
    return instance;
}

void SymbolResolverDebug::initialize() {
    enabled_ = true;
}

void SymbolResolverDebug::shutdown() {
    enabled_ = false;
}

bool SymbolResolverDebug::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::plugin
