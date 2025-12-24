#include <voltron/utility/compiler/code_section_marker.h>
#include <iostream>

namespace voltron::utility::compiler {

CodeSectionMarker& CodeSectionMarker::instance() {
    static CodeSectionMarker instance;
    return instance;
}

void CodeSectionMarker::initialize() {
    enabled_ = true;
    std::cout << "[CodeSectionMarker] Initialized\n";
}

void CodeSectionMarker::shutdown() {
    enabled_ = false;
    std::cout << "[CodeSectionMarker] Shutdown\n";
}

bool CodeSectionMarker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::compiler
