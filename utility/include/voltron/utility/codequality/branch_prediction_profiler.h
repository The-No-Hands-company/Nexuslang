#pragma once

#include <string>
#include <vector>

namespace voltron::utility::codequality {

/**
 * @brief Profile branch predictions
 */
class BranchPredictionProfiler {
public:
    static BranchPredictionProfiler& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    BranchPredictionProfiler() = default;
    ~BranchPredictionProfiler() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::codequality
