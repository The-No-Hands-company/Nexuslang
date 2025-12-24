#include <voltron/utility/reversing/disassembler_helper.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::reversing {

DisassemblerHelper& DisassemblerHelper::instance() {
    static DisassemblerHelper instance;
    return instance;
}

void DisassemblerHelper::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DisassemblerHelper] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DisassemblerHelper::shutdown() {
    enabled_ = false;
    std::cout << "[DisassemblerHelper] Shutdown\n";
}

bool DisassemblerHelper::isEnabled() const {
    return enabled_;
}

void DisassemblerHelper::enable() {
    enabled_ = true;
}

void DisassemblerHelper::disable() {
    enabled_ = false;
}

std::string DisassemblerHelper::getStatus() const {
    std::ostringstream oss;
    oss << "DisassemblerHelper - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DisassemblerHelper::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::reversing
