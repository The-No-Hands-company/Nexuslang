#pragma once

#include <expected>
#include <string>
#include <stacktrace>
#include <source_location>

namespace voltron::utility::error {

/// @brief Enhanced std::expected with diagnostic context
template<typename T, typename E = std::string>
class ExpectedDebug {
public:
    ExpectedDebug(T&& value)
        : expected_(std::forward<T>(value))
        , creation_location_(std::source_location::current())
    {}

    ExpectedDebug(const E& error,
                 std::source_location location = std::source_location::current())
        : expected_(std::unexpected(error))
        , creation_location_(location)
        , error_trace_(std::stacktrace::current(1, 10))
    {}

    bool has_value() const { return expected_.has_value(); }
    explicit operator bool() const { return has_value(); }

    T& value() { return expected_.value(); }
    const T& value() const { return expected_.value(); }

    E& error() { return expected_.error(); }
    const E& error() const { return expected_.error(); }

    const std::stacktrace& getErrorTrace() const { return error_trace_; }
    const std::source_location& getCreationLocation() const { return creation_location_; }

    /// Print detailed error information
    void printError(std::ostream& os) const {
        if (!has_value()) {
            os << "Error: " << error() << "\n";
            os << "Created at: " << creation_location_.file_name()
               << ":" << creation_location_.line() << "\n";
            os << "Stack trace:\n" << error_trace_ << "\n";
        }
    }

private:
    std::expected<T, E> expected_;
    std::source_location creation_location_;
    std::stacktrace error_trace_;
};

} // namespace voltron::utility::error
