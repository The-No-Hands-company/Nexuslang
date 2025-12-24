#pragma once

#include <string>
#include <vector>

namespace voltron::utility::audio {

/**
 * @brief Handle codec errors gracefully
 */
class CodecErrorHandler {
public:
    static CodecErrorHandler& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    CodecErrorHandler() = default;
    ~CodecErrorHandler() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::audio
