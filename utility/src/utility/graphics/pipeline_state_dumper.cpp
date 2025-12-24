#include <voltron/utility/graphics/pipeline_state_dumper.h>
#include <iostream>

namespace voltron::utility::graphics {

PipelineStateDumper& PipelineStateDumper::instance() {
    static PipelineStateDumper instance;
    return instance;
}

void PipelineStateDumper::initialize() {
    enabled_ = true;
    std::cout << "[PipelineStateDumper] Initialized\n";
}

void PipelineStateDumper::shutdown() {
    enabled_ = false;
    std::cout << "[PipelineStateDumper] Shutdown\n";
}

bool PipelineStateDumper::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::graphics
