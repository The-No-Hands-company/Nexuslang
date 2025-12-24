#include <voltron/utility/security/format_string_validator.h>
#include <iostream>

namespace voltron::utility::security {

FormatStringValidator& FormatStringValidator::instance() {
    static FormatStringValidator instance;
    return instance;
}

void FormatStringValidator::initialize() {
    enabled_ = true;
    std::cout << "[FormatStringValidator] Initialized\n";
}

void FormatStringValidator::shutdown() {
    enabled_ = false;
    std::cout << "[FormatStringValidator] Shutdown\n";
}

bool FormatStringValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::security
