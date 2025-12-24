#pragma once

#include <string>
#include <vector>

namespace voltron::utility::plugin {

/**
 * @brief Enhanced dlopen with diagnostics
 */
class DlopenWrapper {
public:
    static DlopenWrapper& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    DlopenWrapper() = default;
    ~DlopenWrapper() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::plugin
