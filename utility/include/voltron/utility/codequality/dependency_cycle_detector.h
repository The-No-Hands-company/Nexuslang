#pragma once

#include <string>
#include <vector>

namespace voltron::utility::codequality {

/**
 * @brief Detect circular dependencies
 */
class DependencyCycleDetector {
public:
    static DependencyCycleDetector& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    DependencyCycleDetector() = default;
    ~DependencyCycleDetector() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::codequality
