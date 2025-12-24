#pragma once

#include <string>
#include <vector>

namespace voltron::utility::algorithmic {

/**
 * @brief Monitor iterative convergence
 */
class ConvergenceMonitor {
public:
    static ConvergenceMonitor& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    ConvergenceMonitor() = default;
    ~ConvergenceMonitor() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::algorithmic
