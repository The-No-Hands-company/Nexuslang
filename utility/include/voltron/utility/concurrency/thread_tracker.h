#pragma once

#include <thread>
#include <unordered_map>
#include <mutex>
#include <string>
#include <vector>

namespace voltron::utility::concurrency {

/// @brief Information about a tracked thread
struct ThreadInfo {
    std::thread::id id;
    std::string name;
    std::chrono::steady_clock::time_point creation_time;
    bool is_alive;
};

/// @brief Track all thread creation and destruction
class ThreadTracker {
public:
    static ThreadTracker& instance();

    /// Register a new thread
    void registerThread(std::thread::id id, const std::string& name);

    /// Unregister a thread (on destruction)
    void unregisterThread(std::thread::id id);

    /// Get information about all threads
    std::vector<ThreadInfo> getAllThreads() const;

    /// Get count of active threads
    size_t getActiveThreadCount() const;

    /// Print thread report
    void printReport(std::ostream& os) const;

private:
    ThreadTracker() = default;

    ThreadTracker(const ThreadTracker&) = delete;
    ThreadTracker& operator=(const ThreadTracker&) = delete;

    mutable std::mutex mutex_;
    std::unordered_map<std::thread::id, ThreadInfo> threads_;
};

/// @brief RAII wrapper for thread tracking
class TrackedThread {
public:
    template<typename F, typename... Args>
    TrackedThread(const std::string& name, F&& f, Args&&... args)
        : name_(name)
        , thread_([this, name, f = std::forward<F>(f),
                  ...args = std::forward<Args>(args)]() mutable {
            ThreadTracker::instance().registerThread(std::this_thread::get_id(), name);
            try {
                f(args...);
            } catch (...) {
                ThreadTracker::instance().unregisterThread(std::this_thread::get_id());
                throw;
            }
            ThreadTracker::instance().unregisterThread(std::this_thread::get_id());
        })
    {}

    ~TrackedThread() {
        if (thread_.joinable()) {
            thread_.join();
        }
    }

    void join() {
        thread_.join();
    }

    bool joinable() const {
        return thread_.joinable();
    }

private:
    std::string name_;
    std::thread thread_;
};

} // namespace voltron::utility::concurrency
