#include <voltron/utility/io/serialization_debug.h>
#include <iostream>

namespace voltron::utility::io {

SerializationDebug& SerializationDebug::instance() {
    static SerializationDebug instance;
    return instance;
}

void SerializationDebug::initialize() {
    enabled_ = true;
    std::cout << "[SerializationDebug] Initialized\n";
}

void SerializationDebug::shutdown() {
    enabled_ = false;
    std::cout << "[SerializationDebug] Shutdown\n";
}

bool SerializationDebug::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::io
