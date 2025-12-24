#pragma once

#include <string>
#include <vector>

namespace voltron::utility::algorithmic {

/**
 * @brief Track compression efficiency
 */
class CompressionRatioTracker {
public:
    static CompressionRatioTracker& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    CompressionRatioTracker() = default;
    ~CompressionRatioTracker() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::algorithmic
