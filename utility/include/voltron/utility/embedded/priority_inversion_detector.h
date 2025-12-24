#pragma once

#include <string>
#include <vector>

namespace voltron::utility::embedded {

/**
 * @brief Detect priority inversions
 */
class PriorityInversionDetector {
public:
    static PriorityInversionDetector& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    PriorityInversionDetector() = default;
    ~PriorityInversionDetector() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::embedded
