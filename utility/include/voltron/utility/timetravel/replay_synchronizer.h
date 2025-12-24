#pragma once

#include <string>
#include <vector>

namespace voltron::utility::timetravel {

/**
 * @brief Synchronize replay with original
 */
class ReplaySynchronizer {
public:
    static ReplaySynchronizer& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    ReplaySynchronizer() = default;
    ~ReplaySynchronizer() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::timetravel
