#pragma once

#include <string>
#include <vector>

namespace voltron::utility::codequality {

/**
 * @brief Export coverage data
 */
class CodeCoverageExporter {
public:
    static CodeCoverageExporter& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    CodeCoverageExporter() = default;
    ~CodeCoverageExporter() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::codequality
