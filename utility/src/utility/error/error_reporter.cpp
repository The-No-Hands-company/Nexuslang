#include <voltron/utility/error/error_reporter.h>
#include <iostream>

namespace voltron::utility::error {

ErrorReporter& ErrorReporter::instance() {
    static ErrorReporter instance;
    return instance;
}

void ErrorReporter::initialize() {
    enabled_ = true;
    std::cout << "[ErrorReporter] Initialized\n";
}

void ErrorReporter::shutdown() {
    enabled_ = false;
    std::cout << "[ErrorReporter] Shutdown\n";
}

bool ErrorReporter::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::error
