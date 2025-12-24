#include "voltron/utility/system/build_info.h"
#include <iostream>

namespace voltron::utility::system {

std::string BuildInfo::getBuildDate() {
    return VOLTRON_BUILD_DATE;
}

std::string BuildInfo::getBuildTime() {
    return VOLTRON_BUILD_TIME;
}

std::string BuildInfo::getCompiler() {
    return VOLTRON_COMPILER;
}

std::string BuildInfo::getVersion() {
    // TODO: Populate from CMake
    return "0.1.0-dev";
}

std::string BuildInfo::getGitHash() {
    // TODO: Populate from CMake/Git
    return "unknown";
}

std::string BuildInfo::getPlatform() {
    return VOLTRON_PLATFORM;
}

void BuildInfo::printAll(std::ostream& os) {
    os << "=== Voltron 3D Build Information ===\n";
    os << "Version:   " << getVersion() << "\n";
    os << "Built:     " << getBuildDate() << " " << getBuildTime() << "\n";
    os << "Compiler:  " << getCompiler() << "\n";
    os << "Platform:  " << getPlatform() << "\n";
    os << "Git Hash:  " << getGitHash() << "\n";
    os << "=====================================\n";
}

} // namespace voltron::utility::system
