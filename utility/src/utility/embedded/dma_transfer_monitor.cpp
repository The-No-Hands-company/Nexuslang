#include <voltron/utility/embedded/dma_transfer_monitor.h>
#include <iostream>

namespace voltron::utility::embedded {

DmaTransferMonitor& DmaTransferMonitor::instance() {
    static DmaTransferMonitor instance;
    return instance;
}

void DmaTransferMonitor::initialize() {
    enabled_ = true;
}

void DmaTransferMonitor::shutdown() {
    enabled_ = false;
}

bool DmaTransferMonitor::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::embedded
