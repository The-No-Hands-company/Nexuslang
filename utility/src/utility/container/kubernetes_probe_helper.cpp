#include <voltron/utility/container/kubernetes_probe_helper.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::container {

KubernetesProbeHelper& KubernetesProbeHelper::instance() {
    static KubernetesProbeHelper instance;
    return instance;
}

void KubernetesProbeHelper::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[KubernetesProbeHelper] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void KubernetesProbeHelper::shutdown() {
    enabled_ = false;
    std::cout << "[KubernetesProbeHelper] Shutdown\n";
}

bool KubernetesProbeHelper::isEnabled() const {
    return enabled_;
}

void KubernetesProbeHelper::enable() {
    enabled_ = true;
}

void KubernetesProbeHelper::disable() {
    enabled_ = false;
}

std::string KubernetesProbeHelper::getStatus() const {
    std::ostringstream oss;
    oss << "KubernetesProbeHelper - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void KubernetesProbeHelper::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::container
