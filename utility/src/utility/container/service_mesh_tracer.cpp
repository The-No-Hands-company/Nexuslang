#include <voltron/utility/container/service_mesh_tracer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::container {

ServiceMeshTracer& ServiceMeshTracer::instance() {
    static ServiceMeshTracer instance;
    return instance;
}

void ServiceMeshTracer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ServiceMeshTracer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ServiceMeshTracer::shutdown() {
    enabled_ = false;
    std::cout << "[ServiceMeshTracer] Shutdown\n";
}

bool ServiceMeshTracer::isEnabled() const {
    return enabled_;
}

void ServiceMeshTracer::enable() {
    enabled_ = true;
}

void ServiceMeshTracer::disable() {
    enabled_ = false;
}

std::string ServiceMeshTracer::getStatus() const {
    std::ostringstream oss;
    oss << "ServiceMeshTracer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ServiceMeshTracer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::container
