#pragma once

#include <string>
#include <chrono>

namespace voltron::utility::system {

/// @brief Build information embedded at compile time
class BuildInfo {
public:
    static std::string getBuildDate();
    static std::string getBuildTime();
    static std::string getCompiler();
    static std::string getVersion();
    static std::string getGitHash();
    static std::string getPlatform();

    /// Print all build info
    static void printAll(std::ostream& os = std::cout);
};

} // namespace voltron::utility::system

// Macros to embed build information
#define VOLTRON_BUILD_DATE __DATE__
#define VOLTRON_BUILD_TIME __TIME__

#if defined(__GNUC__)
    #define VOLTRON_COMPILER "GCC " __VERSION__
#elif defined(__clang__)
    #define VOLTRON_COMPILER "Clang " __clang_version__
#elif defined(_MSC_VER)
    #define VOLTRON_COMPILER "MSVC " _MSC_FULL_VER
#else
    #define VOLTRON_COMPILER "Unknown"
#endif

#if defined(__linux__)
    #define VOLTRON_PLATFORM "Linux"
#elif defined(_WIN32)
    #define VOLTRON_PLATFORM "Windows"
#elif defined(__APPLE__)
    #define VOLTRON_PLATFORM "macOS"
#else
    #define VOLTRON_PLATFORM "Unknown"
#endif
