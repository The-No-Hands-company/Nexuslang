#include "voltron/utility/concurrency/thread_tracker.h"
#include <iostream>
#include <iomanip>

namespace voltron::utility::concurrency {

ThreadTracker& ThreadTracker::instance() {
    static ThreadTracker tracker;
    return tracker;
}

void ThreadTracker::registerThread(std::thread::id id, const std::string& name) {
    std::lock_guard<std::mutex> lock(mutex_);
    ThreadInfo info{
        .id = id,
        .name = name,
        .creation_time = std::chrono::steady_clock::now(),
        .is_alive = true
    };
    threads_[id] = info;
}

void ThreadTracker::unregisterThread(std::thread::id id) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = threads_.find(id);
    if (it != threads_.end()) {
        it->second.is_alive = false;
    }
}

std::vector<ThreadInfo> ThreadTracker::getAllThreads() const {
    std::lock_guard<std::mutex> lock(mutex_);
    std::vector<ThreadInfo> result;
    result.reserve(threads_.size());
    for (const auto& [id, info] : threads_) {
        result.push_back(info);
    }
    return result;
}

size_t ThreadTracker::getActiveThreadCount() const {
    std::lock_guard<std::mutex> lock(mutex_);
    size_t count = 0;
    for (const auto& [id, info] : threads_) {
        if (info.is_alive) ++count;
    }
    return count;
}

void ThreadTracker::printReport(std::ostream& os) const {
    std::lock_guard<std::mutex> lock(mutex_);

    os << "\n=== Thread Tracker Report ===\n";
    os << "Total threads tracked: " << threads_.size() << "\n";
    os << "Active threads: " << getActiveThreadCount() << "\n\n";

    for (const auto& [id, info] : threads_) {
        os << "Thread ID: " << id << "\n";
        os << "  Name: " << info.name << "\n";
        os << "  Status: " << (info.is_alive ? "ALIVE" : "DEAD") << "\n";
        auto now = std::chrono::steady_clock::now();
        auto lifetime = std::chrono::duration_cast<std::chrono::seconds>(
            now - info.creation_time);
        os << "  Lifetime: " << lifetime.count() << "s\n\n";
    }

    os << "=============================\n\n";
}

} // namespace voltron::utility::concurrency
