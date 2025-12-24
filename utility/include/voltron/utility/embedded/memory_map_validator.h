#pragma once

#include <string>
#include <vector>

namespace voltron::utility::embedded {

/**
 * @brief Validate memory layout
 */
class MemoryMapValidator {
public:
    static MemoryMapValidator& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    MemoryMapValidator() = default;
    ~MemoryMapValidator() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::embedded
