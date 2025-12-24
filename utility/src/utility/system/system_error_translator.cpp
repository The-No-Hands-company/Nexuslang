#include <voltron/utility/system/system_error_translator.h>
#include <iostream>

namespace voltron::utility::system {

SystemErrorTranslator& SystemErrorTranslator::instance() {
    static SystemErrorTranslator instance;
    return instance;
}

void SystemErrorTranslator::initialize() {
    enabled_ = true;
    std::cout << "[SystemErrorTranslator] Initialized\n";
}

void SystemErrorTranslator::shutdown() {
    enabled_ = false;
    std::cout << "[SystemErrorTranslator] Shutdown\n";
}

bool SystemErrorTranslator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::system
