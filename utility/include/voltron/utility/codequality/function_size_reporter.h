#pragma once

#include <string>
#include <vector>

namespace voltron::utility::codequality {

/**
 * @brief Report large functions
 */
class FunctionSizeReporter {
public:
    static FunctionSizeReporter& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    FunctionSizeReporter() = default;
    ~FunctionSizeReporter() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::codequality
