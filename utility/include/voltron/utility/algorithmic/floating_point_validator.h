#pragma once

#include <string>
#include <vector>

namespace voltron::utility::algorithmic {

/**
 * @brief Check for NaN/Inf
 */
class FloatingPointValidator {
public:
    static FloatingPointValidator& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    FloatingPointValidator() = default;
    ~FloatingPointValidator() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::algorithmic
