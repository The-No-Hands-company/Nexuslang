#include <voltron/utility/sanitizer/msan_helpers.h>
#include <iostream>

namespace voltron::utility::sanitizer {

MsanHelpers& MsanHelpers::instance() {
    static MsanHelpers instance;
    return instance;
}

void MsanHelpers::initialize() {
    enabled_ = true;
    std::cout << "[MsanHelpers] Initialized\n";
}

void MsanHelpers::shutdown() {
    enabled_ = false;
    std::cout << "[MsanHelpers] Shutdown\n";
}

bool MsanHelpers::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::sanitizer
