#include <voltron/utility/audio/codec_error_handler.h>
#include <iostream>

namespace voltron::utility::audio {

CodecErrorHandler& CodecErrorHandler::instance() {
    static CodecErrorHandler instance;
    return instance;
}

void CodecErrorHandler::initialize() {
    enabled_ = true;
}

void CodecErrorHandler::shutdown() {
    enabled_ = false;
}

bool CodecErrorHandler::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::audio
