#pragma once

#include <string>
#include <vector>

namespace voltron::utility::codequality {

/**
 * @brief Track frequently changed code
 */
class CodeChurnTracker {
public:
    static CodeChurnTracker& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    CodeChurnTracker() = default;
    ~CodeChurnTracker() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::codequality
