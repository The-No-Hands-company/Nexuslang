#pragma once

#include <string>
#include <vector>

namespace voltron::utility::algorithmic {

/**
 * @brief Detect precision loss
 */
class NumericalStabilityChecker {
public:
    static NumericalStabilityChecker& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    NumericalStabilityChecker() = default;
    ~NumericalStabilityChecker() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::algorithmic
