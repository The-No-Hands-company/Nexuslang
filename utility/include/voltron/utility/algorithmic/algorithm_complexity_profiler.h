#pragma once

#include <string>
#include <vector>

namespace voltron::utility::algorithmic {

/**
 * @brief Profile algorithmic complexity
 */
class AlgorithmComplexityProfiler {
public:
    static AlgorithmComplexityProfiler& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    AlgorithmComplexityProfiler() = default;
    ~AlgorithmComplexityProfiler() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::algorithmic
