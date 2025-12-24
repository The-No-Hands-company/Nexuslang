#include "voltron/utility/logging/structured_logger.h"
#include <iomanip>

namespace voltron::utility::logging {

namespace {
    std::string escapeJSON(const std::string& s) {
        std::ostringstream o;
        for (auto c : s) {
            switch (c) {
                case '"': o << "\\\""; break;
                case '\\': o << "\\\\"; break;
                case '\b': o << "\\b"; break;
                case '\f': o << "\\f"; break;
                case '\n': o << "\\n"; break;
                case '\r': o << "\\r"; break;
                case '\t': o << "\\t"; break;
                default:
                    if ('\x00' <= c && c <= '\x1f') {
                        o << "\\u"
                          << std::hex << std::setw(4) << std::setfill('0') << (int)c;
                    } else {
                        o << c;
                    }
            }
        }
        return o.str();
    }
}

LogBuilder& LogBuilder::add(const std::string& key, const std::string& value) {
    fields_.push_back({key, "\"" + escapeJSON(value) + "\""});
    return *this;
}

LogBuilder& LogBuilder::add(const std::string& key, int value) {
    fields_.push_back({key, std::to_string(value)});
    return *this;
}

LogBuilder& LogBuilder::add(const std::string& key, double value) {
    fields_.push_back({key, std::to_string(value)});
    return *this;
}

LogBuilder& LogBuilder::add(const std::string& key, bool value) {
    fields_.push_back({key, value ? "true" : "false"});
    return *this;
}

std::string LogBuilder::toJSON() const {
    std::ostringstream oss;
    oss << "{";
    for (size_t i = 0; i < fields_.size(); ++i) {
        oss << "\"" << escapeJSON(fields_[i].first) << "\": " << fields_[i].second;
        if (i < fields_.size() - 1) oss << ", ";
    }
    oss << "}";
    return oss.str();
}

StructuredLogger& StructuredLogger::instance() {
    static StructuredLogger logger;
    return logger;
}

void StructuredLogger::log(LogLevel level, const std::string& event, const LogBuilder& data, std::source_location location) {
    // Construct JSON
    // { "timestamp": "...", "level": "INFO", "event": "UserLogin", "data": { ... }, "source": "..." }
    
    // We reuse Logger infrastructure by passing formatted JSON as message,
    // assuming Logger plain text formatter will just wrap it.
    // Or we want pure JSON output?
    // If we want pure JSON, Logger needs a "Raw" mode or we should bypass Logger's formatter.
    // For now, let's just log it as a message.
    
    std::ostringstream msg;
    msg << "[JSON] event=\"" << event << "\" data=" << data.toJSON();
    
    Logger::instance().log(level, msg.str(), location);
}

void StructuredLogger::log(LogLevel level, const std::string& event, const std::map<std::string, std::string>& data, std::source_location location) {
    LogBuilder builder;
    for (const auto& [k, v] : data) {
        builder.add(k, v);
    }
    log(level, event, builder, location);
}

} // namespace voltron::utility::logging
