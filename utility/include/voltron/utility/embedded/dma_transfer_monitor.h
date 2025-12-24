#pragma once

#include <string>
#include <vector>

namespace voltron::utility::embedded {

/**
 * @brief Monitor DMA operations
 */
class DmaTransferMonitor {
public:
    static DmaTransferMonitor& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    DmaTransferMonitor() = default;
    ~DmaTransferMonitor() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::embedded
