#pragma once

#include "voltron/utility/logging/logger.h"

/// @file log_macros.h
/// @brief Convenient logging macros with automatic source location

#define VOLTRON_LOG_TRACE(msg) \
    voltron::utility::logging::Logger::instance().log( \
        voltron::utility::logging::LogLevel::Trace, msg)

#define VOLTRON_LOG_DEBUG(msg) \
    voltron::utility::logging::Logger::instance().log( \
        voltron::utility::logging::LogLevel::Debug, msg)

#define VOLTRON_LOG_INFO(msg) \
    voltron::utility::logging::Logger::instance().log( \
        voltron::utility::logging::LogLevel::Info, msg)

#define VOLTRON_LOG_WARN(msg) \
    voltron::utility::logging::Logger::instance().log( \
        voltron::utility::logging::LogLevel::Warning, msg)

#define VOLTRON_LOG_ERROR(msg) \
    voltron::utility::logging::Logger::instance().log( \
        voltron::utility::logging::LogLevel::Error, msg)

#define VOLTRON_LOG_CRITICAL(msg) \
    voltron::utility::logging::Logger::instance().log( \
        voltron::utility::logging::LogLevel::Critical, msg)

// Formatted logging macros
#define VOLTRON_LOG_TRACE_FMT(...) \
    VOLTRON_LOG_TRACE((std::ostringstream{} << __VA_ARGS__).str())

#define VOLTRON_LOG_DEBUG_FMT(...) \
    VOLTRON_LOG_DEBUG((std::ostringstream{} << __VA_ARGS__).str())

#define VOLTRON_LOG_INFO_FMT(...) \
    VOLTRON_LOG_INFO((std::ostringstream{} << __VA_ARGS__).str())

#define VOLTRON_LOG_WARN_FMT(...) \
    VOLTRON_LOG_WARN((std::ostringstream{} << __VA_ARGS__).str())

#define VOLTRON_LOG_ERROR_FMT(...) \
    VOLTRON_LOG_ERROR((std::ostringstream{} << __VA_ARGS__).str())

#define VOLTRON_LOG_CRITICAL_FMT(...) \
    VOLTRON_LOG_CRITICAL((std::ostringstream{} << __VA_ARGS__).str())
