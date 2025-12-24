#include "voltron/utility/event/event_bus.h"
#include <iostream>
#include <iomanip>

namespace voltron::utility::event {

void EventLogger::logEvent(const std::string& event_name, const std::string& details) {
    log_.push_back({
        std::chrono::steady_clock::now(),
        event_name,
        details
    });
}

const std::vector<EventLogger::EventRecord>& EventLogger::getLog() const {
    return log_;
}

void EventLogger::printLog(std::ostream& os, size_t max_events) const {
    os << "\n=== Event Log ===\n";

    size_t start = log_.size() > max_events ? log_.size() - max_events : 0;

    for (size_t i = start; i < log_.size(); ++i) {
        const auto& record = log_[i];

        // Format timestamp
        auto epoch = record.timestamp.time_since_epoch();
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(epoch).count();

        os << "[" << std::setw(10) << ms << "ms] "
           << record.event_name;

        if (!record.details.empty()) {
            os << ": " << record.details;
        }

        os << "\n";
    }

    os << "=================\n";
}

void EventLogger::clear() {
    log_.clear();
}

} // namespace voltron::utility::event
