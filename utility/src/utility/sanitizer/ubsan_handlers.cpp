#include <voltron/utility/sanitizer/ubsan_handlers.h>
#include <iostream>

namespace voltron::utility::sanitizer {

UbsanHandlers& UbsanHandlers::instance() {
    static UbsanHandlers instance;
    return instance;
}

void UbsanHandlers::initialize() {
    enabled_ = true;
    std::cout << "[UbsanHandlers] Initialized\n";
}

void UbsanHandlers::shutdown() {
    enabled_ = false;
    std::cout << "[UbsanHandlers] Shutdown\n";
}

bool UbsanHandlers::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::sanitizer
