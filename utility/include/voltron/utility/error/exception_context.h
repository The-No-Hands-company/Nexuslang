#pragma once

#include <exception>
#include <string>
#include <unordered_map>
#include <any>
#include <source_location>

namespace voltron::utility::error {

/// @brief Attach contextual data to exceptions
class ExceptionContext {
public:
    /// Add context data
    template<typename T>
    void addContext(const std::string& key, const T& value) {
        context_[key] = value;
    }

    /// Get context data
    template<typename T>
    std::optional<T> getContext(const std::string& key) const {
        auto it = context_.find(key);
        if (it != context_.end()) {
            try {
                return std::any_cast<T>(it->second);
            } catch (const std::bad_any_cast&) {
                return std::nullopt;
            }
        }
        return std::nullopt;
    }

    /// Get all context keys
    std::vector<std::string> getKeys() const;

    /// Print all context data
    void print(std::ostream& os) const;

private:
    std::unordered_map<std::string, std::any> context_;
};

/// @brief Exception with attached context
class ContextualException : public std::exception {
public:
    explicit ContextualException(const std::string& message,
                                std::source_location location = std::source_location::current())
        : message_(message)
        , location_(location)
    {}

    const char* what() const noexcept override {
        return message_.c_str();
    }

    ExceptionContext& context() { return context_; }
    const ExceptionContext& context() const { return context_; }

    const std::source_location& location() const { return location_; }

    /// Print exception with full context
    void printFull(std::ostream& os) const;

private:
    std::string message_;
    std::source_location location_;
    ExceptionContext context_;
};

} // namespace voltron::utility::error
