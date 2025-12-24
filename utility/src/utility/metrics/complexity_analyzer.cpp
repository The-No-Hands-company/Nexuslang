#include "voltron/utility/metrics/complexity_analyzer.h"
#include <iostream>
#include <cmath>
#include <numeric>
#include <algorithm>

namespace voltron::utility::metrics {

ComplexityAnalyzer::FunctionMetrics
ComplexityAnalyzer::analyzeFunction(const std::string& source_code) {
    FunctionMetrics metrics;

    // Simplified analysis - production would use proper parser
    metrics.line_count = std::count(source_code.begin(), source_code.end(), '\n') + 1;
    metrics.cyclomatic_complexity = estimateCyclomaticComplexity(source_code);
    metrics.max_nesting_depth = countNestingDepth(source_code);

    return metrics;
}

size_t ComplexityAnalyzer::estimateCyclomaticComplexity(const std::string& source_code) {
    // McCabe's cyclomatic complexity: count decision points
    size_t complexity = 1;  // Base complexity

    // Count decision keywords
    const std::vector<std::string> keywords = {
        "if", "else if", "for", "while", "case", "catch", "&&", "||", "?"
    };

    for (const auto& keyword : keywords) {
        size_t pos = 0;
        while ((pos = source_code.find(keyword, pos)) != std::string::npos) {
            complexity++;
            pos += keyword.length();
        }
    }

    return complexity;
}

size_t ComplexityAnalyzer::countNestingDepth(const std::string& source_code) {
    size_t max_depth = 0;
    size_t current_depth = 0;

    for (char ch : source_code) {
        if (ch == '{') {
            current_depth++;
            max_depth = std::max(max_depth, current_depth);
        } else if (ch == '}') {
            if (current_depth > 0) current_depth--;
        }
    }

    return max_depth;
}

void CoverageTracker::markLineExecuted(const std::string& file, int line_number) {
    files_[file].executed_lines.insert(line_number);
}

void CoverageTracker::registerLine(const std::string& file, int line_number) {
    files_[file].all_lines.insert(line_number);
}

CoverageTracker::CoverageStats CoverageTracker::getStats(const std::string& file) const {
    CoverageStats stats;

    if (file.empty()) {
        // Aggregate stats for all files
        for (const auto& [filename, info] : files_) {
            stats.total_lines += info.all_lines.size();
            stats.executed_lines += info.executed_lines.size();
        }
    } else {
        auto it = files_.find(file);
        if (it != files_.end()) {
            stats.total_lines = it->second.all_lines.size();
            stats.executed_lines = it->second.executed_lines.size();
        }
    }

    if (stats.total_lines > 0) {
        stats.coverage_percent = (static_cast<float>(stats.executed_lines) /
                                 static_cast<float>(stats.total_lines)) * 100.0f;
    }

    return stats;
}

void CoverageTracker::printReport(std::ostream& os) const {
    os << "\n=== Code Coverage Report ===\n";

    for (const auto& [file, info] : files_) {
        auto stats = getStats(file);
        os << file << ": "
           << stats.executed_lines << "/" << stats.total_lines
           << " (" << std::fixed << std::setprecision(1) << stats.coverage_percent << "%)\n";
    }

    auto total = getStats();
    os << "\nTotal: "
       << total.executed_lines << "/" << total.total_lines
       << " (" << std::fixed << std::setprecision(1) << total.coverage_percent << "%)\n";
    os << "============================\n";
}

void CoverageTracker::clear() {
    files_.clear();
}

void PerformanceMetrics::recordMetric(const std::string& name, double value) {
    metrics_[name].values.push_back(value);
}

PerformanceMetrics::Stats PerformanceMetrics::getStats(const std::string& name) const {
    auto it = metrics_.find(name);
    if (it == metrics_.end()) {
        return {};
    }

    const auto& values = it->second.values;
    if (values.empty()) {
        return {};
    }

    Stats stats;
    stats.count = values.size();
    stats.min = *std::min_element(values.begin(), values.end());
    stats.max = *std::max_element(values.begin(), values.end());

    // Calculate mean
    double sum = std::accumulate(values.begin(), values.end(), 0.0);
    stats.mean = sum / values.size();

    // Calculate standard deviation
    double sq_sum = 0.0;
    for (double val : values) {
        double diff = val - stats.mean;
        sq_sum += diff * diff;
    }
    stats.stddev = std::sqrt(sq_sum / values.size());

    return stats;
}

void PerformanceMetrics::printReport(std::ostream& os) const {
    os << "\n=== Performance Metrics ===\n";

    for (const auto& [name, data] : metrics_) {
        auto stats = getStats(name);
        os << name << ":\n"
           << "  Count: " << stats.count << "\n"
           << "  Min: " << stats.min << "\n"
           << "  Max: " << stats.max << "\n"
           << "  Mean: " << stats.mean << "\n"
           << "  StdDev: " << stats.stddev << "\n";
    }

    os << "===========================\n";
}

void PerformanceMetrics::clear() {
    metrics_.clear();
}

} // namespace voltron::utility::metrics
