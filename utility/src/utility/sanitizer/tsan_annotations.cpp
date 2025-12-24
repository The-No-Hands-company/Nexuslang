#include <voltron/utility/sanitizer/tsan_annotations.h>
#include <iostream>

namespace voltron::utility::sanitizer {

TsanAnnotations& TsanAnnotations::instance() {
    static TsanAnnotations instance;
    return instance;
}

void TsanAnnotations::initialize() {
    enabled_ = true;
    std::cout << "[TsanAnnotations] Initialized\n";
}

void TsanAnnotations::shutdown() {
    enabled_ = false;
    std::cout << "[TsanAnnotations] Shutdown\n";
}

bool TsanAnnotations::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::sanitizer
