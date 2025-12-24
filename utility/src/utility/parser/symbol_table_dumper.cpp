#include <voltron/utility/parser/symbol_table_dumper.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::parser {

SymbolTableDumper& SymbolTableDumper::instance() {
    static SymbolTableDumper instance;
    return instance;
}

void SymbolTableDumper::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[SymbolTableDumper] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void SymbolTableDumper::shutdown() {
    enabled_ = false;
    std::cout << "[SymbolTableDumper] Shutdown\n";
}

bool SymbolTableDumper::isEnabled() const {
    return enabled_;
}

void SymbolTableDumper::enable() {
    enabled_ = true;
}

void SymbolTableDumper::disable() {
    enabled_ = false;
}

std::string SymbolTableDumper::getStatus() const {
    std::ostringstream oss;
    oss << "SymbolTableDumper - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void SymbolTableDumper::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::parser
