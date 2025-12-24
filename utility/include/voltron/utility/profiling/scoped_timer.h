#pragma once

#include <chrono>
#include <string>
#include <iostream>

namespace voltron::utility::profiling {

/// @brief RAII-based timer for measuring code block execution time
class ScopedTimer {
public:
    explicit ScopedTimer(const std::string& name, bool print_on_destruction = true)
        : name_(name)
        , print_on_destruction_(print_on_destruction)
        , start_(std::chrono::high_resolution_clock::now())
    {}

    ~ScopedTimer() {
        if (print_on_destruction_) {
            auto duration = elapsed();
            std::cout << "[ScopedTimer '" << name_ << "'] "
                     << duration.count() << "ms\n";
        }
    }

    /// Get elapsed time without destroying the timer
    std::chrono::microseconds elapsed() const {
        auto end = std::chrono::high_resolution_clock::now();
        return std::chrono::duration_cast<std::chrono::microseconds>(end - start_);
    }

    /// Reset the timer
    void reset() {
        start_ = std::chrono::high_resolution_clock::now();
    }

private:
    std::string name_;
    bool print_on_destruction_;
    std::chrono::high_resolution_clock::time_point start_;
};

/// @brief Macro for convenient timer creation
#define VOLTRON_PROFILE_SCOPE(name) \
    voltron::utility::profiling::ScopedTimer _timer_##__LINE__(name)

#define VOLTRON_PROFILE_FUNCTION() \
    voltron::utility::profiling::ScopedTimer _timer_##__LINE__(__FUNCTION__)

} // namespace voltron::utility::profiling
