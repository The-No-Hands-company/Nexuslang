#include <voltron/utility/debug/disassembly_helper.h>
#include <iostream>

namespace voltron::utility::debug {

DisassemblyHelper& DisassemblyHelper::instance() {
    static DisassemblyHelper instance;
    return instance;
}

void DisassemblyHelper::initialize() {
    enabled_ = true;
    std::cout << "[DisassemblyHelper] Initialized\n";
}

void DisassemblyHelper::shutdown() {
    enabled_ = false;
    std::cout << "[DisassemblyHelper] Shutdown\n";
}

bool DisassemblyHelper::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::debug
