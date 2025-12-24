#include <voltron/utility/codequality/function_size_reporter.h>
#include <iostream>

namespace voltron::utility::codequality {

FunctionSizeReporter& FunctionSizeReporter::instance() {
    static FunctionSizeReporter instance;
    return instance;
}

void FunctionSizeReporter::initialize() {
    enabled_ = true;
}

void FunctionSizeReporter::shutdown() {
    enabled_ = false;
}

bool FunctionSizeReporter::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::codequality
