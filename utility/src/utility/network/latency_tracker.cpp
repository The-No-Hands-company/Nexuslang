#include "voltron/utility/network/latency_tracker.h"
#include <algorithm>
#include <iostream>
#include <iomanip>

namespace voltron::utility::network {

NetworkErrorCategory NetworkErrorClassifier::classify(int error_code) {
    // Platform-specific error code mapping
    // This is simplified - real implementation would use errno values
    switch (error_code) {
        case 110: return NetworkErrorCategory::Timeout;
        case 111: return NetworkErrorCategory::ConnectionRefused;
        case 104: return NetworkErrorCategory::ConnectionReset;
        case 113: return NetworkErrorCategory::HostUnreachable;
        default:  return NetworkErrorCategory::Unknown;
    }
}

std::string NetworkErrorClassifier::categoryToString(NetworkErrorCategory category) {
    switch (category) {
        case NetworkErrorCategory::Timeout: return "Timeout";
        case NetworkErrorCategory::ConnectionRefused: return "Connection Refused";
        case NetworkErrorCategory::ConnectionReset: return "Connection Reset";
        case NetworkErrorCategory::HostUnreachable: return "Host Unreachable";
        case NetworkErrorCategory::DNSFailure: return "DNS Failure";
        case NetworkErrorCategory::SSLError: return "SSL Error";
        case NetworkErrorCategory::Unknown: return "Unknown";
    }
    return "Unknown";
}

void LatencyTracker::recordLatency(const std::string& endpoint,
                                   std::chrono::microseconds latency) {
    std::lock_guard<std::mutex> lock(mutex_);
    latencies_[endpoint].push_back(latency);
}

LatencyTracker::LatencyStats LatencyTracker::getStats(const std::string& endpoint) const {
    std::lock_guard<std::mutex> lock(mutex_);

    auto it = latencies_.find(endpoint);
    if (it == latencies_.end() || it->second.empty()) {
        return {};
    }

    auto latencies = it->second;
    std::sort(latencies.begin(), latencies.end());

    LatencyStats stats;
    stats.count = latencies.size();
    stats.min = latencies.front();
    stats.max = latencies.back();

    // Calculate average
    auto sum = std::chrono::microseconds{0};
    for (const auto& lat : latencies) {
        sum += lat;
    }
    stats.avg = sum / latencies.size();

    // Percentiles
    stats.p50 = latencies[latencies.size() * 50 / 100];
    stats.p95 = latencies[latencies.size() * 95 / 100];
    stats.p99 = latencies[latencies.size() * 99 / 100];

    return stats;
}

void LatencyTracker::printReport(std::ostream& os) const {
    std::lock_guard<std::mutex> lock(mutex_);

    os << "\n=== Network Latency Report ===\n";
    for (const auto& [endpoint, _] : latencies_) {
        auto stats = getStats(endpoint);
        os << "Endpoint: " << endpoint << "\n";
        os << "  Count: " << stats.count << "\n";
        os << "  Min: " << stats.min.count() << "μs\n";
        os << "  Avg: " << stats.avg.count() << "μs\n";
        os << "  P50: " << stats.p50.count() << "μs\n";
        os << "  P95: " << stats.p95.count() << "μs\n";
        os << "  P99: " << stats.p99.count() << "μs\n";
        os << "  Max: " << stats.max.count() << "μs\n\n";
    }
    os << "==============================\n";
}

void CircuitBreakerMonitor::recordSuccess(const std::string& service) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto& state = services_[service];
    state.success_count++;

    // Transition from HalfOpen to Closed after successes
    if (state.state == State::HalfOpen && state.success_count >= 3) {
        state.state = State::Closed;
        state.failure_count = 0;
    }
}

void CircuitBreakerMonitor::recordFailure(const std::string& service) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto& state = services_[service];
    state.failure_count++;
    state.last_failure = std::chrono::steady_clock::now();

    // Transition to Open after threshold failures
    if (state.failure_count >= 5) {
        state.state = State::Open;
    }
}

CircuitBreakerMonitor::State CircuitBreakerMonitor::getState(const std::string& service) const {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = services_.find(service);
    if (it == services_.end()) {
        return State::Closed;
    }

    auto& state = it->second;

    // Auto-transition from Open to HalfOpen after timeout
    if (state.state == State::Open) {
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(
            now - state.last_failure);
        if (elapsed.count() >= 30) {  // 30 second timeout
            const_cast<ServiceState&>(state).state = State::HalfOpen;
        }
    }

    return state.state;
}

void CircuitBreakerMonitor::printReport(std::ostream& os) const {
    std::lock_guard<std::mutex> lock(mutex_);

    os << "\n=== Circuit Breaker Report ===\n";
    for (const auto& [service, state] : services_) {
        os << "Service: " << service << "\n";
        os << "  State: ";
        switch (state.state) {
            case State::Closed: os << "CLOSED (healthy)\n"; break;
            case State::Open: os << "OPEN (failing)\n"; break;
            case State::HalfOpen: os << "HALF-OPEN (testing)\n"; break;
        }
        os << "  Failures: " << state.failure_count << "\n";
        os << "  Successes: " << state.success_count << "\n\n";
    }
    os << "==============================\n";
}

} // namespace voltron::utility::network
