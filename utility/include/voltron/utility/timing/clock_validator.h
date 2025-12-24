#pragma once

#include <chrono>
#include <string>
#include <functional>
#include <mutex>

namespace voltron::utility::timing {

/// @brief Detect clock skew and timing issues
class ClockValidator {
public:
    /// Check if system clock has jumped
    static bool detectClockJump(std::chrono::milliseconds threshold = std::chrono::seconds(5));

    /// Check monotonic clock guarantees
    static bool isMonotonicClockReliable();

    /// Print clock information
    static void printClockInfo(std::ostream& os);
};

/// @brief Track missed deadlines
class DeadlineMonitor {
public:
    using DeadlineCallback = std::function<void(const std::string&, std::chrono::microseconds)>;

    void setDeadline(const std::string& task_name, std::chrono::microseconds deadline);
    void recordTaskStart(const std::string& task_name);
    void recordTaskEnd(const std::string& task_name);

    void setMissedDeadlineCallback(DeadlineCallback callback);

    struct DeadlineStats {
        size_t total_runs = 0;
        size_t missed_count = 0;
        std::chrono::microseconds avg_duration{};
        std::chrono::microseconds max_duration{};
    };

    DeadlineStats getStats(const std::string& task_name) const;
    void printReport(std::ostream& os) const;

private:
    struct TaskInfo {
        std::chrono::microseconds deadline{};
        std::chrono::steady_clock::time_point start_time;
        std::vector<std::chrono::microseconds> durations;
        size_t missed_count = 0;
    };

    mutable std::mutex mutex_;
    std::unordered_map<std::string, TaskInfo> tasks_;
    DeadlineCallback callback_;
};

/// @brief Analyze timing jitter
class JitterAnalyzer {
public:
    void recordInterval(std::chrono::microseconds interval);

    struct JitterStats {
        std::chrono::microseconds mean{};
        std::chrono::microseconds stddev{};
        std::chrono::microseconds min_jitter{};
        std::chrono::microseconds max_jitter{};
    };

    JitterStats getStats() const;
    void reset();

private:
    mutable std::mutex mutex_;
    std::vector<std::chrono::microseconds> intervals_;
};

/// @brief Monitor game loop or event loop timing
class TickRateMonitor {
public:
    void tick();

    double getCurrentFPS() const;
    double getAverageFPS() const;
    std::chrono::microseconds getFrameTime() const;

    void printReport(std::ostream& os) const;

private:
    mutable std::mutex mutex_;
    std::chrono::steady_clock::time_point last_tick_;
    std::chrono::steady_clock::time_point start_time_;
    size_t tick_count_ = 0;
    std::chrono::microseconds last_frame_time_{};
};

} // namespace voltron::utility::timing
