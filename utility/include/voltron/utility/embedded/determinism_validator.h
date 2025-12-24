#pragma once

#include <string>
#include <vector>

namespace voltron::utility::embedded {

/**
 * @brief Ensure deterministic execution
 */
class DeterminismValidator {
public:
    static DeterminismValidator& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    DeterminismValidator() = default;
    ~DeterminismValidator() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::embedded
