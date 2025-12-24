#include <voltron/utility/debug/variable_dumper.h>
#include <iostream>

namespace voltron::utility::debug {

VariableDumper& VariableDumper::instance() {
    static VariableDumper instance;
    return instance;
}

void VariableDumper::initialize() {
    enabled_ = true;
    std::cout << "[VariableDumper] Initialized\n";
}

void VariableDumper::shutdown() {
    enabled_ = false;
    std::cout << "[VariableDumper] Shutdown\n";
}

bool VariableDumper::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::debug
