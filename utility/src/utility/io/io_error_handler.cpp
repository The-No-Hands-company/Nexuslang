#include <voltron/utility/io/io_error_handler.h>
#include <iostream>

namespace voltron::utility::io {

IoErrorHandler& IoErrorHandler::instance() {
    static IoErrorHandler instance;
    return instance;
}

void IoErrorHandler::initialize() {
    enabled_ = true;
    std::cout << "[IoErrorHandler] Initialized\n";
}

void IoErrorHandler::shutdown() {
    enabled_ = false;
    std::cout << "[IoErrorHandler] Shutdown\n";
}

bool IoErrorHandler::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::io
