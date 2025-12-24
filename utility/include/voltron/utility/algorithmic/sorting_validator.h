#pragma once

#include <string>
#include <vector>

namespace voltron::utility::algorithmic {

/**
 * @brief Validate sort correctness
 */
class SortingValidator {
public:
    static SortingValidator& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    SortingValidator() = default;
    ~SortingValidator() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::algorithmic
