#pragma once

#include <string>
#include <vector>

namespace voltron::utility::codequality {

/**
 * @brief Analyze component coupling
 */
class CouplingAnalyzer {
public:
    static CouplingAnalyzer& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    CouplingAnalyzer() = default;
    ~CouplingAnalyzer() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::codequality
