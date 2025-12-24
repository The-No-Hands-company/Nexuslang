#include <voltron/utility/codequality/code_coverage_exporter.h>
#include <iostream>

namespace voltron::utility::codequality {

CodeCoverageExporter& CodeCoverageExporter::instance() {
    static CodeCoverageExporter instance;
    return instance;
}

void CodeCoverageExporter::initialize() {
    enabled_ = true;
}

void CodeCoverageExporter::shutdown() {
    enabled_ = false;
}

bool CodeCoverageExporter::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::codequality
