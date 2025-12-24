#pragma once

#include <string>
#include <vector>

namespace voltron::utility::codequality {

/**
 * @brief Runtime complexity metrics
 */
class CyclomaticComplexityTracker {
public:
    static CyclomaticComplexityTracker& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    CyclomaticComplexityTracker() = default;
    ~CyclomaticComplexityTracker() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::codequality
