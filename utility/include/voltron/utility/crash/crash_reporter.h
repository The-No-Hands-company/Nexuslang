#pragma once

#include <string>
#include <vector>
#include <source_location>
#include <functional>

namespace voltron::utility::crash {

/**
 * @brief Comprehensive crash reporter with context collection
 * 
 * Generates detailed crash reports including:
 * - Stack traces
 * - Register states
 * - Thread information
 * - Memory snapshots
 * - Application state
 */
class CrashReporter {
public:
    struct CrashReport {
        int signal_number;
        std::string signal_name;
        std::string stack_trace;
        std::string timestamp;
        std::string executable_path;
        std::string working_directory;
        std::vector<std::string> thread_info;
        std::vector<std::pair<std::string, std::string>> custom_context;
    };

    using CrashCallback = std::function<void(const CrashReport&)>;

    static CrashReporter& instance();

    /**
     * @brief Add custom context to crash reports
     */
    void addContext(const std::string& key, const std::string& value);

    /**
     * @brief Set callback for crash handling
     */
    void setCrashCallback(CrashCallback callback);

    /**
     * @brief Generate crash report (called from signal handler)
     */
    CrashReport generateReport(int signal);

    /**
     * @brief Save crash report to file
     */
    bool saveCrashDump(const CrashReport& report, const std::string& filepath);

    /**
     * @brief Enable minidump generation (platform-specific)
     */
    void enableMinidumps(const std::string& dump_directory);

private:
    CrashReporter() = default;
    
    std::vector<std::pair<std::string, std::string>> context_;
    CrashCallback callback_;
    std::string dump_directory_;
};

} // namespace voltron::utility::crash
