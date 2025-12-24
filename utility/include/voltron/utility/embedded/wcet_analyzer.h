#pragma once

#include <string>
#include <vector>

namespace voltron::utility::embedded {

/**
 * @brief Worst-case execution time tracking
 */
class WcetAnalyzer {
public:
    static WcetAnalyzer& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    WcetAnalyzer() = default;
    ~WcetAnalyzer() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::embedded
