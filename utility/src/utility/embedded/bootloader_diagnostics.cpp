#include <voltron/utility/embedded/bootloader_diagnostics.h>
#include <iostream>

namespace voltron::utility::embedded {

BootloaderDiagnostics& BootloaderDiagnostics::instance() {
    static BootloaderDiagnostics instance;
    return instance;
}

void BootloaderDiagnostics::initialize() {
    enabled_ = true;
}

void BootloaderDiagnostics::shutdown() {
    enabled_ = false;
}

bool BootloaderDiagnostics::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::embedded
