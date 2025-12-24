#include <voltron/utility/error/error_code_wrapper.h>
#include <iostream>

namespace voltron::utility::error {

ErrorCodeWrapper& ErrorCodeWrapper::instance() {
    static ErrorCodeWrapper instance;
    return instance;
}

void ErrorCodeWrapper::initialize() {
    enabled_ = true;
    std::cout << "[ErrorCodeWrapper] Initialized\n";
}

void ErrorCodeWrapper::shutdown() {
    enabled_ = false;
    std::cout << "[ErrorCodeWrapper] Shutdown\n";
}

bool ErrorCodeWrapper::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::error
