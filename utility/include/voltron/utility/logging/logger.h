#pragma once

#include <string>
#include <vector>
#include <mutex>
#include <memory>
#include <source_location>
#include <voltron/utility/logging/log_sinks.h>

namespace voltron::utility::logging {

enum class LogLevel {
    Trace,
    Debug,
    Info,
    Warning,
    Error,
    Critical
};

class Logger {
public:
    static Logger& instance();

    void log(LogLevel level, const std::string& message,
             std::source_location location = std::source_location::current());

    // Sink management
    void addSink(std::shared_ptr<LogSink> sink);
    void clearSinks();

    // Convenience setup
    void addConsoleSink();
    void addFileSink(const std::string& filename);
    void addRotatingFileSink(const std::string& filename, size_t max_size, int max_files);

    void setLogLevel(LogLevel level);
    LogLevel getLogLevel() const;

    void setTimestamps(bool enabled);
    void flush();

private:
    Logger();
    ~Logger();

    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

    std::string formatMessage(LogLevel level, const std::string& message,
                             const std::source_location& location) const;
    const char* levelToString(LogLevel level) const;

    mutable std::mutex mutex_;
    LogLevel min_level_ = LogLevel::Info;
    bool timestamps_ = true;
    
    std::vector<std::shared_ptr<LogSink>> sinks_;
};

} // namespace voltron::utility::logging

// Macros for convenient logging
#define VOLTRON_LOG_TRACE(msg) voltron::utility::logging::Logger::instance().log(voltron::utility::logging::LogLevel::Trace, msg)
#define VOLTRON_LOG_DEBUG(msg) voltron::utility::logging::Logger::instance().log(voltron::utility::logging::LogLevel::Debug, msg)
#define VOLTRON_LOG_INFO(msg)  voltron::utility::logging::Logger::instance().log(voltron::utility::logging::LogLevel::Info, msg)
#define VOLTRON_LOG_WARN(msg)  voltron::utility::logging::Logger::instance().log(voltron::utility::logging::LogLevel::Warning, msg)
#define VOLTRON_LOG_ERROR(msg) voltron::utility::logging::Logger::instance().log(voltron::utility::logging::LogLevel::Error, msg)
#define VOLTRON_LOG_CRIT(msg)  voltron::utility::logging::Logger::instance().log(voltron::utility::logging::LogLevel::Critical, msg)
