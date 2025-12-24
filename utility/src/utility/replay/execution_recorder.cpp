#include "voltron/utility/replay/execution_recorder.h"
#include <fstream>
#include <iostream>
#include <iomanip>

namespace voltron::utility::replay {

void ExecutionRecorder::startRecording() {
    recording_ = true;
    recording_start_ = std::chrono::steady_clock::now();
    events_.clear();
}

void ExecutionRecorder::stopRecording() {
    recording_ = false;
}

bool ExecutionRecorder::isRecording() const {
    return recording_;
}

void ExecutionRecorder::recordEvent(const std::string& function_name,
                                   const std::string& event_type,
                                   const std::string& data) {
    if (!recording_) return;

    events_.push_back({
        std::chrono::steady_clock::now(),
        function_name,
        event_type,
        data
    });
}

const std::vector<ExecutionRecorder::Event>& ExecutionRecorder::getEvents() const {
    return events_;
}

void ExecutionRecorder::saveToFile(const std::string& filename) const {
    std::ofstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open file for writing");
    }

    for (const auto& event : events_) {
        auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(
            event.timestamp - recording_start_);

        file << elapsed.count() << ","
             << event.function_name << ","
             << event.event_type << ","
             << event.data << "\n";
    }
}

void ExecutionRecorder::loadFromFile(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open file for reading");
    }

    events_.clear();
    recording_start_ = std::chrono::steady_clock::now();

    std::string line;
    while (std::getline(file, line)) {
        // Simple CSV parsing - production code would be more robust
        size_t pos1 = line.find(',');
        size_t pos2 = line.find(',', pos1 + 1);
        size_t pos3 = line.find(',', pos2 + 1);

        if (pos1 == std::string::npos || pos2 == std::string::npos) continue;

        long long elapsed_us = std::stoll(line.substr(0, pos1));
        std::string func = line.substr(pos1 + 1, pos2 - pos1 - 1);
        std::string type = line.substr(pos2 + 1, pos3 - pos2 - 1);
        std::string data = (pos3 != std::string::npos) ? line.substr(pos3 + 1) : "";

        events_.push_back({
            recording_start_ + std::chrono::microseconds(elapsed_us),
            func,
            type,
            data
        });
    }
}

void ExecutionRecorder::clear() {
    events_.clear();
}

CallHistoryBuffer::CallHistoryBuffer(size_t max_size)
    : max_size_(max_size)
{
    buffer_.resize(max_size);
}

void CallHistoryBuffer::recordCall(const std::string& function_name,
                                  const std::vector<std::string>& arguments,
                                  const std::string& return_value) {
    buffer_[write_index_] = {
        std::chrono::steady_clock::now(),
        function_name,
        arguments,
        return_value
    };

    write_index_ = (write_index_ + 1) % max_size_;
}

std::vector<CallHistoryBuffer::CallRecord>
CallHistoryBuffer::getRecentCalls(size_t count) const {
    std::vector<CallRecord> recent;
    count = std::min(count, max_size_);

    for (size_t i = 0; i < count; ++i) {
        size_t index = (write_index_ + max_size_ - count + i) % max_size_;
        if (!buffer_[index].function_name.empty()) {
            recent.push_back(buffer_[index]);
        }
    }

    return recent;
}

void CallHistoryBuffer::printHistory(std::ostream& os, size_t count) const {
    auto recent = getRecentCalls(count);

    os << "\n=== Call History (Last " << recent.size() << " calls) ===\n";
    for (const auto& record : recent) {
        os << record.function_name << "(";
        for (size_t i = 0; i < record.arguments.size(); ++i) {
            if (i > 0) os << ", ";
            os << record.arguments[i];
        }
        os << ")";
        if (!record.return_value.empty()) {
            os << " -> " << record.return_value;
        }
        os << "\n";
    }
    os << "==========================================\n";
}

void CallHistoryBuffer::clear() {
    buffer_.clear();
    buffer_.resize(max_size_);
    write_index_ = 0;
}

} // namespace voltron::utility::replay
