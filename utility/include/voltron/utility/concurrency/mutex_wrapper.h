#pragma once

#include <mutex>
#include <chrono>
#include <string>
#include <iostream>

namespace voltron::utility::concurrency {

/// @brief Mutex wrapper with contention reporting
template<typename MutexType = std::mutex>
class MutexWrapper {
public:
    explicit MutexWrapper(const std::string& name) : name_(name) {}

    void lock() {
        auto start = std::chrono::high_resolution_clock::now();
        mutex_.lock();
        auto end = std::chrono::high_resolution_clock::now();

        auto wait_time = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

#ifdef VOLTRON_DEBUG_MUTEX_CONTENTION
        if (wait_time.count() > 1000) {  // More than 1ms wait
            std::cerr << "[MutexWrapper '" << name_ << "'] High contention detected: "
                     << wait_time.count() << "μs wait time\n";
        }
#endif

        ++lock_count_;
        total_wait_time_ += wait_time;
    }

    void unlock() {
        mutex_.unlock();
    }

    bool try_lock() {
        return mutex_.try_lock();
    }

    const std::string& getName() const { return name_; }
    size_t getLockCount() const { return lock_count_; }
    std::chrono::microseconds getTotalWaitTime() const { return total_wait_time_; }

private:
    MutexType mutex_;
    std::string name_;
    size_t lock_count_ = 0;
    std::chrono::microseconds total_wait_time_{0};
};

} // namespace voltron::utility::concurrency
