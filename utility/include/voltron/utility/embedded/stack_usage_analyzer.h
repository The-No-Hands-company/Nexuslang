#pragma once

#include <string>
#include <vector>

namespace voltron::utility::embedded {

/**
 * @brief Monitor stack consumption
 */
class StackUsageAnalyzer {
public:
    static StackUsageAnalyzer& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    StackUsageAnalyzer() = default;
    ~StackUsageAnalyzer() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::embedded
