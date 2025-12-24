#pragma once

#include <string>
#include <vector>

namespace voltron::utility::codequality {

/**
 * @brief Find unreachable code paths
 */
class DeadCodeDetector {
public:
    static DeadCodeDetector& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    DeadCodeDetector() = default;
    ~DeadCodeDetector() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::codequality
