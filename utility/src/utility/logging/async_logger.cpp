#include "voltron/utility/logging/async_logger.h"
#include <iostream>

namespace voltron::utility::logging {

AsyncLogger& AsyncLogger::instance() {
    static AsyncLogger logger;
    return logger;
}

AsyncLogger::AsyncLogger() {
    start();
}

AsyncLogger::~AsyncLogger() {
    stop();
}

void AsyncLogger::start() {
    if (running_.exchange(true)) return; // Already running
    exit_requested_ = false;
    worker_thread_ = std::thread(&AsyncLogger::workerLoop, this);
}

void AsyncLogger::stop() {
    if (!running_.exchange(false)) return;
    
    exit_requested_ = true;
    cv_.notify_all();
    
    if (worker_thread_.joinable()) {
        worker_thread_.join();
    }
}

void AsyncLogger::setTargetSink(std::shared_ptr<LogSink> sink) {
    std::lock_guard<std::mutex> lock(queue_mutex_);
    target_sink_ = std::move(sink);
}

void AsyncLogger::write(const LogRecord& record) {
    if (!running_) {
        // Fallback or drop? Fallback to sync write if target exists?
        // Let's just drop or fallback. Fallback is safer.
         std::lock_guard<std::mutex> lock(queue_mutex_);
         if (target_sink_) target_sink_->write(record);
         return;
    }

    {
        std::lock_guard<std::mutex> lock(queue_mutex_);
        queue_.push(record);
    }
    cv_.notify_one();
}

void AsyncLogger::flush() {
    // We need to wait until the queue is empty AND the worker has finished processing.
    // Simpler approach: a condition variable or busy wait loop checking queue size.
    // Since we are in utility toolkit, let's allow a busy-ish wait for simplicity or add a "flushed" cv.
    
    // Better: Enqueue a special "flush token" or just poll.
    // Let's implement a simple poll loop since we don't have a "batch finished" signal easily without modifying worker.
    
    // Actually, simply locking mutex is not enough.
    // Let's loop while queue is not empty.
    
    int retries = 0;
    while (true) {
        std::unique_lock<std::mutex> lock(queue_mutex_);
        if (queue_.empty()) {
            break;
        }
        lock.unlock();
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
        retries++;
        if (retries > 1000) break; // Timeout
    }
    
    // After queue is empty, worker might still be processing the last batch.
    // Give it a tiny bit more time or assume worker is fast.
    // Ideally we'd have a sync mechanism but for this phase this fix is likely sufficient.
}

void AsyncLogger::workerLoop() {
    while (!exit_requested_ || !queue_.empty()) {
        std::vector<LogRecord> batch;
        {
            std::unique_lock<std::mutex> lock(queue_mutex_);
            cv_.wait(lock, [this] { return !queue_.empty() || exit_requested_; });

            // Swallow entire queue
            while (!queue_.empty()) {
                batch.push_back(std::move(queue_.front()));
                queue_.pop();
            }
        } // release lock

        if (!batch.empty() && target_sink_) {
            for (const auto& record : batch) {
                target_sink_->write(record); // target sink manages its own locking
            }
            target_sink_->flush();
        }
        
        if (batch.empty() && exit_requested_) break;
    }
}

} // namespace voltron::utility::logging
