#include <voltron/utility/cpp23/ranges_pipeline_tracer.h>
#include <iostream>

namespace voltron::utility::cpp23 {

RangesPipelineTracer& RangesPipelineTracer::instance() {
    static RangesPipelineTracer instance;
    return instance;
}

void RangesPipelineTracer::initialize() {
    enabled_ = true;
    std::cout << "[RangesPipelineTracer] Initialized\n";
}

void RangesPipelineTracer::shutdown() {
    enabled_ = false;
    std::cout << "[RangesPipelineTracer] Shutdown\n";
}

bool RangesPipelineTracer::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::cpp23
