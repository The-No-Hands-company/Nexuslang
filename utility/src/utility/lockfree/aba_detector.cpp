#include "voltron/utility/lockfree/aba_detector.h"
#include <iostream>
#include <iomanip>

namespace voltron::utility::lockfree {

void MemoryOrderValidator::recordOperation(Operation op,
                                          std::memory_order order,
                                          const std::string& variable_name) {
    operations_.push_back({op, order, variable_name});
}

bool MemoryOrderValidator::validateOrdering(std::vector<std::string>& warnings_out) const {
    bool valid = true;

    for (const auto& record : operations_) {
        // Check for common mistakes
        if (record.op == Operation::Load) {
            if (record.order == std::memory_order_release ||
                record.order == std::memory_order_acq_rel) {
                warnings_out.push_back("Load with release semantics: " + record.variable_name);
                valid = false;
            }
        }

        if (record.op == Operation::Store) {
            if (record.order == std::memory_order_acquire ||
                record.order == std::memory_order_acq_rel) {
                warnings_out.push_back("Store with acquire semantics: " + record.variable_name);
                valid = false;
            }
        }

        // Warn about relaxed ordering
        if (record.order == std::memory_order_relaxed) {
            warnings_out.push_back("Relaxed ordering used (verify correctness): " + record.variable_name);
        }
    }

    return valid;
}

void MemoryOrderValidator::printReport(std::ostream& os) const {
    os << "\n=== Memory Ordering Report ===\n";

    const char* op_names[] = {"Load", "Store", "CompareExchange", "FetchAdd"};
    const char* order_names[] = {
        "relaxed", "consume", "acquire", "release", "acq_rel", "seq_cst"
    };

    for (const auto& record : operations_) {
        os << op_names[static_cast<int>(record.op)] << " "
           << record.variable_name << " with "
           << order_names[static_cast<int>(record.order)] << " ordering\n";
    }

    os << "===============================\n";
}

void LockFreeProgressMonitor::recordThreadAttempt(size_t thread_id, bool success) {
    auto& stats = thread_stats_[thread_id];
    stats.attempts++;

    if (success) {
        stats.successes++;
        stats.consecutive_failures = 0;
    } else {
        stats.consecutive_failures++;
        stats.max_consecutive_failures = std::max(
            stats.max_consecutive_failures,
            stats.consecutive_failures
        );
    }
}

LockFreeProgressMonitor::ProgressGuarantee
LockFreeProgressMonitor::estimateGuarantee() const {
    bool all_threads_progress = true;
    bool system_progresses = false;

    for (const auto& [thread_id, stats] : thread_stats_) {
        if (stats.successes > 0) {
            system_progresses = true;
        }

        if (stats.max_consecutive_failures > 100) {
            all_threads_progress = false;
        }
    }

    if (all_threads_progress) {
        return ProgressGuarantee::WaitFree;
    } else if (system_progresses) {
        return ProgressGuarantee::LockFree;
    }

    return ProgressGuarantee::Blocking;
}

LockFreeProgressMonitor::ProgressStats LockFreeProgressMonitor::getStats() const {
    ProgressStats total;

    for (const auto& [thread_id, stats] : thread_stats_) {
        total.total_attempts += stats.attempts;
        total.successful_attempts += stats.successes;
        total.failed_attempts += (stats.attempts - stats.successes);
        total.max_retries = std::max(total.max_retries, stats.max_consecutive_failures);
    }

    return total;
}

void LockFreeProgressMonitor::printReport(std::ostream& os) const {
    auto stats = getStats();
    auto guarantee = estimateGuarantee();

    os << "\n=== Lock-Free Progress Report ===\n";

    const char* guarantee_names[] = {
        "Wait-Free", "Lock-Free", "Obstruction-Free", "Blocking"
    };

    os << "Estimated guarantee: " << guarantee_names[static_cast<int>(guarantee)] << "\n";
    os << "Total attempts: " << stats.total_attempts << "\n";
    os << "Successful: " << stats.successful_attempts << "\n";
    os << "Failed: " << stats.failed_attempts << "\n";
    os << "Max retries: " << stats.max_retries << "\n";

    os << "\nPer-thread stats:\n";
    for (const auto& [thread_id, tstats] : thread_stats_) {
        os << "  Thread " << thread_id << ": "
           << tstats.successes << "/" << tstats.attempts
           << " (max failures: " << tstats.max_consecutive_failures << ")\n";
    }

    os << "==================================\n";
}

void CompareExchangeTracer::recordCAS(const std::string& variable_name,
                                     bool success,
                                     const std::string& location) {
    cas_history_.push_back({
        variable_name,
        success,
        location,
        std::chrono::steady_clock::now()
    });
}

std::vector<CompareExchangeTracer::CASStats> CompareExchangeTracer::getStats() const {
    std::unordered_map<std::string, CASStats> stats_map;

    for (const auto& record : cas_history_) {
        auto& stats = stats_map[record.variable_name];
        stats.variable_name = record.variable_name;
        stats.total_attempts++;

        if (record.success) {
            stats.successes++;
        } else {
            stats.failures++;
        }
    }

    std::vector<CASStats> result;
    for (auto& [name, stats] : stats_map) {
        if (stats.total_attempts > 0) {
            stats.success_rate = static_cast<float>(stats.successes) /
                                static_cast<float>(stats.total_attempts) * 100.0f;
        }
        result.push_back(stats);
    }

    return result;
}

void CompareExchangeTracer::printReport(std::ostream& os) const {
    auto stats = getStats();

    os << "\n=== Compare-Exchange Statistics ===\n";
    os << std::setw(30) << "Variable"
       << std::setw(10) << "Attempts"
       << std::setw(10) << "Success"
       << std::setw(10) << "Failed"
       << std::setw(12) << "Success %\n";
    os << std::string(72, '-') << "\n";

    for (const auto& s : stats) {
        os << std::setw(30) << s.variable_name
           << std::setw(10) << s.total_attempts
           << std::setw(10) << s.successes
           << std::setw(10) << s.failures
           << std::setw(12) << std::fixed << std::setprecision(1)
           << s.success_rate << "%\n";
    }

    os << "====================================\n";
}

} // namespace voltron::utility::lockfree
