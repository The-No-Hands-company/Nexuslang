#include "voltron/utility/logging/logger.h"
#include <iostream>
#include <iomanip>
#include <chrono>

namespace voltron::utility::logging {

Logger& Logger::instance() {
    static Logger logger;
    return logger;
}

Logger::Logger() {
    // Default to console sink if no others? 
    // Or users must configure. Let's add console by default for usability.
    addConsoleSink();
}

Logger::~Logger() {
    flush();
}

void Logger::log(LogLevel level, const std::string& message, std::source_location location) {
    // Quick check to avoid formatting if not needed
    // Note: thread safety issue here if writing min_level_ but reading is atomic-ish.
    // For strict correctness we need lock or atomic. 
    // Let's lock inside getLogLevel() or just lock here.
    if (level < getLogLevel()) return;

    // Format message
    // We do formatting under lock or before?
    // Before lock is better for concurrency if sinks take long, but sinks need lock anyway.
    // Let's format first.
    std::string formatted;
    {
         // formatMessage uses const members, need to check if they are protected
         // timestamps_ and logic inside needed protection? 
         // timestamps_ is modified by setTimestamps. 
         std::lock_guard<std::mutex> lock(mutex_);
         formatted = formatMessage(level, message, location);
    }
    
    LogRecord record{message, level, formatted};

    std::vector<std::shared_ptr<LogSink>> sinks_copy;
    {
        std::lock_guard<std::mutex> lock(mutex_);
        sinks_copy = sinks_;
    }

    // Write to sinks (sinks are thread-safe or locked internally usually, 
    // but here we are calling them sequentially).
    for (auto& sink : sinks_copy) {
        sink->write(record);
    }
}

void Logger::addSink(std::shared_ptr<LogSink> sink) {
    std::lock_guard<std::mutex> lock(mutex_);
    sinks_.push_back(std::move(sink));
}

void Logger::clearSinks() {
    std::lock_guard<std::mutex> lock(mutex_);
    sinks_.clear();
}

void Logger::addConsoleSink() {
    addSink(std::make_shared<ConsoleSink>());
}

void Logger::addFileSink(const std::string& filename) {
    addSink(std::make_shared<FileSink>(filename));
}

void Logger::addRotatingFileSink(const std::string& filename, size_t max_size, int max_files) {
    addSink(std::make_shared<RotatingFileSink>(filename, max_size, max_files));
}

void Logger::setLogLevel(LogLevel level) {
    std::lock_guard<std::mutex> lock(mutex_);
    min_level_ = level;
}

LogLevel Logger::getLogLevel() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return min_level_;
}

void Logger::setTimestamps(bool enabled) {
    std::lock_guard<std::mutex> lock(mutex_);
    timestamps_ = enabled;
}

void Logger::flush() {
    std::vector<std::shared_ptr<LogSink>> sinks_copy;
    {
         std::lock_guard<std::mutex> lock(mutex_);
         sinks_copy = sinks_;
    }
    for (auto& sink : sinks_copy) {
        sink->flush();
    }
}

std::string Logger::formatMessage(LogLevel level, const std::string& message,
                                 const std::source_location& location) const {
    std::ostringstream oss;

    if (timestamps_) {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            now.time_since_epoch()) % 1000;

        // Use safe localtime
        struct tm tm_buf;
        localtime_r(&time_t, &tm_buf); // POSIX

        oss << "[" << std::put_time(&tm_buf, "%Y-%m-%d %H:%M:%S")
            << "." << std::setfill('0') << std::setw(3) << ms.count() << "] ";
    }

    oss << "[" << levelToString(level) << "] ";
    // Optional: strip full path from file name for cleaner logs
    std::string file_name = location.file_name();
    // primitive basename
    size_t last_slash = file_name.find_last_of("/\\");
    if (last_slash != std::string::npos) {
        file_name = file_name.substr(last_slash + 1);
    }
    
    oss << "[" << file_name << ":" << location.line() << "] ";
    oss << message;

    return oss.str();
}

const char* Logger::levelToString(LogLevel level) const {
    switch (level) {
        case LogLevel::Trace:    return "TRACE";
        case LogLevel::Debug:    return "DEBUG";
        case LogLevel::Info:     return "INFO ";
        case LogLevel::Warning:  return "WARN ";
        case LogLevel::Error:    return "ERROR";
        case LogLevel::Critical: return "CRIT ";
        default:                 return "UNKNOWN";
    }
}

} // namespace voltron::utility::logging
