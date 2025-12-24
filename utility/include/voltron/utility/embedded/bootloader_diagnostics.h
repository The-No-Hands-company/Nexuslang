#pragma once

#include <string>
#include <vector>

namespace voltron::utility::embedded {

/**
 * @brief Early-boot diagnostics
 */
class BootloaderDiagnostics {
public:
    static BootloaderDiagnostics& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    BootloaderDiagnostics() = default;
    ~BootloaderDiagnostics() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::embedded
