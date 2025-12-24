#include <voltron/utility/reflection/struct_printer.h>
#include <iostream>

namespace voltron::utility::reflection {

StructPrinter& StructPrinter::instance() {
    static StructPrinter instance;
    return instance;
}

void StructPrinter::initialize() {
    enabled_ = true;
    std::cout << "[StructPrinter] Initialized\n";
}

void StructPrinter::shutdown() {
    enabled_ = false;
    std::cout << "[StructPrinter] Shutdown\n";
}

bool StructPrinter::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::reflection
