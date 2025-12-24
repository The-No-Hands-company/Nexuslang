#include <voltron/utility/assertions/runtime_validator.h>
#include <iostream>

namespace voltron::utility::assertions {

RuntimeValidator& RuntimeValidator::instance() {
    static RuntimeValidator instance;
    return instance;
}

void RuntimeValidator::initialize() {
    enabled_ = true;
    std::cout << "[RuntimeValidator] Initialized\n";
}

void RuntimeValidator::shutdown() {
    enabled_ = false;
    std::cout << "[RuntimeValidator] Shutdown\n";
}

bool RuntimeValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::assertions
