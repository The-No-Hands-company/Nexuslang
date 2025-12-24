#pragma once

#include <string>
#include <vector>

namespace voltron::utility::plugin {

/**
 * @brief Validate plugin ABI compatibility
 */
class AbiValidator {
public:
    static AbiValidator& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    AbiValidator() = default;
    ~AbiValidator() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::plugin
