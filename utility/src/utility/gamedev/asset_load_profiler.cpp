#include <voltron/utility/gamedev/asset_load_profiler.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::gamedev {

AssetLoadProfiler& AssetLoadProfiler::instance() {
    static AssetLoadProfiler instance;
    return instance;
}

void AssetLoadProfiler::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AssetLoadProfiler] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AssetLoadProfiler::shutdown() {
    enabled_ = false;
    std::cout << "[AssetLoadProfiler] Shutdown\n";
}

bool AssetLoadProfiler::isEnabled() const {
    return enabled_;
}

void AssetLoadProfiler::enable() {
    enabled_ = true;
}

void AssetLoadProfiler::disable() {
    enabled_ = false;
}

std::string AssetLoadProfiler::getStatus() const {
    std::ostringstream oss;
    oss << "AssetLoadProfiler - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AssetLoadProfiler::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::gamedev
