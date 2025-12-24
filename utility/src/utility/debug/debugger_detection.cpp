#include "voltron/utility/debug/debugger_detection.h"
#include <fstream>
#include <string>

#ifdef __linux__
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace voltron::utility::debug {

bool DebuggerDetection::isDebuggerPresent() {
#ifdef __linux__
    // Check /proc/self/status for TracerPid
    std::ifstream status_file("/proc/self/status");
    std::string line;
    while (std::getline(status_file, line)) {
        if (line.find("TracerPid:") == 0) {
            std::string pid_str = line.substr(10);
            int tracer_pid = std::stoi(pid_str);
            return tracer_pid != 0;
        }
    }
    return false;
#elif defined(_WIN32)
    return IsDebuggerPresent();
#else
    // Platform not supported
    return false;
#endif
}

void DebuggerDetection::printStatus(std::ostream& os) {
    os << "Debugger status: " << (isDebuggerPresent() ? "ATTACHED" : "NOT ATTACHED") << "\n";
}

} // namespace voltron::utility::debug
