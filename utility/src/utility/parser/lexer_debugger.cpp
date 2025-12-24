#include <voltron/utility/parser/lexer_debugger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::parser {

LexerDebugger& LexerDebugger::instance() {
    static LexerDebugger instance;
    return instance;
}

void LexerDebugger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[LexerDebugger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void LexerDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[LexerDebugger] Shutdown\n";
}

bool LexerDebugger::isEnabled() const {
    return enabled_;
}

void LexerDebugger::enable() {
    enabled_ = true;
}

void LexerDebugger::disable() {
    enabled_ = false;
}

std::string LexerDebugger::getStatus() const {
    std::ostringstream oss;
    oss << "LexerDebugger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void LexerDebugger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::parser
