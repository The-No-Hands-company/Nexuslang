#include <voltron/utility/reflection/enum_to_string.h>
#include <iostream>

namespace voltron::utility::reflection {

EnumToString& EnumToString::instance() {
    static EnumToString instance;
    return instance;
}

void EnumToString::initialize() {
    enabled_ = true;
    std::cout << "[EnumToString] Initialized\n";
}

void EnumToString::shutdown() {
    enabled_ = false;
    std::cout << "[EnumToString] Shutdown\n";
}

bool EnumToString::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::reflection
