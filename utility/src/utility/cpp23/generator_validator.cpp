#include <voltron/utility/cpp23/generator_validator.h>
#include <iostream>

namespace voltron::utility::cpp23 {

GeneratorValidator& GeneratorValidator::instance() {
    static GeneratorValidator instance;
    return instance;
}

void GeneratorValidator::initialize() {
    enabled_ = true;
    std::cout << "[GeneratorValidator] Initialized\n";
}

void GeneratorValidator::shutdown() {
    enabled_ = false;
    std::cout << "[GeneratorValidator] Shutdown\n";
}

bool GeneratorValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::cpp23
