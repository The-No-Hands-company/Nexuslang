#include "voltron/utility/timing/clock_validator.h"
#include <iostream>
#include <iomanip>
#include <numeric>
#include <cmath>

namespace voltron::utility::timing {

static std::chrono::steady_clock::time_point last_check_time = std::chrono::steady_clock::now();

bool ClockValidator::detectClockJump(std::chrono::milliseconds threshold) {
    auto now = std::chrono::steady_clock::now();
    auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - last_check_time);

    bool jumped = elapsed > threshold || elapsed < std::chrono::milliseconds(0);
    last_check_time = now;

    return jumped;
}

bool ClockValidator::isMonotonicClockReliable() {
    return std::chrono::steady_clock::is_steady;
}

void ClockValidator::printClockInfo(std::ostream& os) {
    os << "\n=== Clock Information ===\n";
    os << "System clock:\n";
    os << "  is_steady: " << (std::chrono::system_clock::is_steady ? "yes" : "no") << "\n";
    os << "Steady clock:\n";
    os << "  is_steady: " << (std::chrono::steady_clock::is_steady ? "yes" : "no") << "\n";
    os << "High resolution clock:\n";
    os << "  is_steady: " << (std::chrono::high_resolution_clock::is_steady ? "yes" : "no") << "\n";
    os << "=========================\n";
}

void DeadlineMonitor::setDeadline(const std::string& task_name,
                                 std::chrono::microseconds deadline) {
    std::lock_guard<std::mutex> lock(mutex_);
    tasks_[task_name].deadline = deadline;
}

void DeadlineMonitor::recordTaskStart(const std::string& task_name) {
    std::lock_guard<std::mutex> lock(mutex_);
    tasks_[task_name].start_time = std::chrono::steady_clock::now();
}

void DeadlineMonitor::recordTaskEnd(const std::string& task_name) {
    std::lock_guard<std::mutex> lock(mutex_);

    auto& info = tasks_[task_name];
    auto now = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
        now - info.start_time);

    info.durations.push_back(duration);

    if (duration > info.deadline) {
        info.missed_count++;
        if (callback_) {
            callback_(task_name, duration - info.deadline);
        }
    }
}

void DeadlineMonitor::setMissedDeadlineCallback(DeadlineCallback callback) {
    std::lock_guard<std::mutex> lock(mutex_);
    callback_ = std::move(callback);
}

DeadlineMonitor::DeadlineStats DeadlineMonitor::getStats(const std::string& task_name) const {
    std::lock_guard<std::mutex> lock(mutex_);

    auto it = tasks_.find(task_name);
    if (it == tasks_.end()) {
        return {};
    }

    const auto& info = it->second;
    DeadlineStats stats;
    stats.total_runs = info.durations.size();
    stats.missed_count = info.missed_count;

    if (!info.durations.empty()) {
        auto sum = std::accumulate(info.durations.begin(), info.durations.end(),
                                  std::chrono::microseconds{0});
        stats.avg_duration = sum / info.durations.size();
        stats.max_duration = *std::max_element(info.durations.begin(), info.durations.end());
    }

    return stats;
}

void DeadlineMonitor::printReport(std::ostream& os) const {
    std::lock_guard<std::mutex> lock(mutex_);

    os << "\n=== Deadline Monitor Report ===\n";
    for (const auto& [task_name, info] : tasks_) {
        auto stats = getStats(task_name);
        os << "Task: " << task_name << "\n";
        os << "  Deadline: " << info.deadline.count() << "μs\n";
        os << "  Total runs: " << stats.total_runs << "\n";
        os << "  Missed: " << stats.missed_count << " ("
           << (stats.total_runs > 0 ? (100.0 * stats.missed_count / stats.total_runs) : 0)
           << "%)\n";
        os << "  Avg duration: " << stats.avg_duration.count() << "μs\n";
        os << "  Max duration: " << stats.max_duration.count() << "μs\n\n";
    }
    os << "================================\n";
}

void JitterAnalyzer::recordInterval(std::chrono::microseconds interval) {
    std::lock_guard<std::mutex> lock(mutex_);
    intervals_.push_back(interval);
}

JitterAnalyzer::JitterStats JitterAnalyzer::getStats() const {
    std::lock_guard<std::mutex> lock(mutex_);

    if (intervals_.empty()) {
        return {};
    }

    // Calculate mean
    auto sum = std::accumulate(intervals_.begin(), intervals_.end(),
                              std::chrono::microseconds{0});
    auto mean = sum / intervals_.size();

    // Calculate standard deviation
    double variance = 0.0;
    for (const auto& interval : intervals_) {
        double diff = (interval - mean).count();
        variance += diff * diff;
    }
    variance /= intervals_.size();
    auto stddev = std::chrono::microseconds(static_cast<long long>(std::sqrt(variance)));

    JitterStats stats;
    stats.mean = mean;
    stats.stddev = stddev;
    stats.min_jitter = *std::min_element(intervals_.begin(), intervals_.end());
    stats.max_jitter = *std::max_element(intervals_.begin(), intervals_.end());

    return stats;
}

void JitterAnalyzer::reset() {
    std::lock_guard<std::mutex> lock(mutex_);
    intervals_.clear();
}

void TickRateMonitor::tick() {
    std::lock_guard<std::mutex> lock(mutex_);

    auto now = std::chrono::steady_clock::now();

    if (tick_count_ == 0) {
        start_time_ = now;
    } else {
        last_frame_time_ = std::chrono::duration_cast<std::chrono::microseconds>(
            now - last_tick_);
    }

    last_tick_ = now;
    tick_count_++;
}

double TickRateMonitor::getCurrentFPS() const {
    std::lock_guard<std::mutex> lock(mutex_);
    if (last_frame_time_.count() == 0) return 0.0;
    return 1000000.0 / last_frame_time_.count();
}

double TickRateMonitor::getAverageFPS() const {
    std::lock_guard<std::mutex> lock(mutex_);
    if (tick_count_ <= 1) return 0.0;

    auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(
        last_tick_ - start_time_);
    return (tick_count_ - 1) * 1000000.0 / elapsed.count();
}

std::chrono::microseconds TickRateMonitor::getFrameTime() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return last_frame_time_;
}

void TickRateMonitor::printReport(std::ostream& os) const {
    std::lock_guard<std::mutex> lock(mutex_);

    os << "\n=== Tick Rate Report ===\n";
    os << "Total ticks: " << tick_count_ << "\n";
    os << "Current FPS: " << std::fixed << std::setprecision(2)
       << getCurrentFPS() << "\n";
    os << "Average FPS: " << std::fixed << std::setprecision(2)
       << getAverageFPS() << "\n";
    os << "Frame time: " << last_frame_time_.count() << "μs\n";
    os << "========================\n";
}

} // namespace voltron::utility::timing
