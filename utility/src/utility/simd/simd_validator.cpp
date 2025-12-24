#include "voltron/utility/simd/simd_validator.h"
#include <iostream>
#include <iomanip>
#include <cmath>

#ifdef _MSC_VER
#include <intrin.h>
#else
#include <cpuid.h>
#endif

namespace voltron::utility::simd {

// Static member initialization
CPUFeatureDetector::Features CPUFeatureDetector::cached_features_;
bool CPUFeatureDetector::features_detected_ = false;

bool SIMDValidator::validateFloatArray(const float* data, size_t size) {
    for (size_t i = 0; i < size; ++i) {
        if (std::isnan(data[i]) || std::isinf(data[i])) {
            return false;
        }
    }
    return true;
}

bool SIMDValidator::validateDoubleArray(const double* data, size_t size) {
    for (size_t i = 0; i < size; ++i) {
        if (std::isnan(data[i]) || std::isinf(data[i])) {
            return false;
        }
    }
    return true;
}

CPUFeatureDetector::Features CPUFeatureDetector::detect() {
    if (features_detected_) {
        return cached_features_;
    }

    Features features;

#if defined(__x86_64__) || defined(_M_X64) || defined(__i386) || defined(_M_IX86)
    // x86/x64 CPUID detection
    uint32_t eax, ebx, ecx, edx;

    #ifdef _MSC_VER
        int cpuInfo[4];
        __cpuid(cpuInfo, 1);
        ecx = cpuInfo[2];
        edx = cpuInfo[3];
    #else
        __get_cpuid(1, &eax, &ebx, &ecx, &edx);
    #endif

    features.sse = (edx & (1 << 25)) != 0;
    features.sse2 = (edx & (1 << 26)) != 0;
    features.sse3 = (ecx & (1 << 0)) != 0;
    features.ssse3 = (ecx & (1 << 9)) != 0;
    features.sse4_1 = (ecx & (1 << 19)) != 0;
    features.sse4_2 = (ecx & (1 << 20)) != 0;
    features.avx = (ecx & (1 << 28)) != 0;
    features.fma = (ecx & (1 << 12)) != 0;

    #ifdef _MSC_VER
        __cpuid(cpuInfo, 7);
        ebx = cpuInfo[1];
    #else
        __get_cpuid_count(7, 0, &eax, &ebx, &ecx, &edx);
    #endif

    features.avx2 = (ebx & (1 << 5)) != 0;
    features.avx512f = (ebx & (1 << 16)) != 0;

#elif defined(__ARM_NEON) || defined(__aarch64__)
    features.neon = true;
#endif

    cached_features_ = features;
    features_detected_ = true;

    return features;
}

void CPUFeatureDetector::printFeatures(std::ostream& os) {
    auto features = detect();

    os << "\n=== CPU SIMD Features ===\n";

    if (features.sse) os << "✓ SSE\n";
    if (features.sse2) os << "✓ SSE2\n";
    if (features.sse3) os << "✓ SSE3\n";
    if (features.ssse3) os << "✓ SSSE3\n";
    if (features.sse4_1) os << "✓ SSE4.1\n";
    if (features.sse4_2) os << "✓ SSE4.2\n";
    if (features.avx) os << "✓ AVX\n";
    if (features.avx2) os << "✓ AVX2\n";
    if (features.avx512f) os << "✓ AVX-512F\n";
    if (features.fma) os << "✓ FMA\n";
    if (features.neon) os << "✓ NEON (ARM)\n";

    os << "=========================\n";
}

bool CPUFeatureDetector::hasSSE() {
    return detect().sse;
}

bool CPUFeatureDetector::hasAVX() {
    return detect().avx;
}

bool CPUFeatureDetector::hasAVX2() {
    return detect().avx2;
}

bool CPUFeatureDetector::hasAVX512() {
    return detect().avx512f;
}

bool CPUFeatureDetector::hasNEON() {
    return detect().neon;
}

void VectorizationChecker::recordLoop(const std::string& function_name,
                                     int line_number,
                                     bool vectorized,
                                     const std::string& reason) {
    loops_.push_back({function_name, line_number, vectorized, reason});
}

void VectorizationChecker::printReport(std::ostream& os) const {
    os << "\n=== Vectorization Report ===\n";
    os << "Total loops: " << loops_.size() << "\n";
    os << "Vectorized: " << getVectorizedCount() << "\n";
    os << "Not vectorized: " << (loops_.size() - getVectorizedCount()) << "\n\n";

    os << "Details:\n";
    for (const auto& loop : loops_) {
        os << (loop.vectorized ? "✓" : "✗") << " "
           << loop.function_name << ":" << loop.line_number;

        if (!loop.reason.empty()) {
            os << " - " << loop.reason;
        }
        os << "\n";
    }

    os << "============================\n";
}

size_t VectorizationChecker::getVectorizedCount() const {
    return std::count_if(loops_.begin(), loops_.end(),
        [](const LoopInfo& info) { return info.vectorized; });
}

void VectorizationProfiler::recordScalarTime(const std::string& operation,
                                            std::chrono::nanoseconds time) {
    scalar_times_[operation] = time;
}

void VectorizationProfiler::recordVectorTime(const std::string& operation,
                                            std::chrono::nanoseconds time) {
    vector_times_[operation] = time;
}

std::vector<VectorizationProfiler::SpeedupStats> VectorizationProfiler::getSpeedups() const {
    std::vector<SpeedupStats> stats;

    for (const auto& [op, scalar_time] : scalar_times_) {
        auto it = vector_times_.find(op);
        if (it != vector_times_.end()) {
            SpeedupStats s;
            s.operation = op;
            s.scalar_time = scalar_time;
            s.vector_time = it->second;
            s.speedup = static_cast<double>(scalar_time.count()) /
                       static_cast<double>(it->second.count());
            stats.push_back(s);
        }
    }

    return stats;
}

void VectorizationProfiler::printReport(std::ostream& os) const {
    auto speedups = getSpeedups();

    os << "\n=== Vectorization Performance ===\n";
    os << std::setw(30) << "Operation"
       << std::setw(15) << "Scalar (ns)"
       << std::setw(15) << "Vector (ns)"
       << std::setw(10) << "Speedup" << "\n";
    os << std::string(70, '-') << "\n";

    for (const auto& s : speedups) {
        os << std::setw(30) << s.operation
           << std::setw(15) << s.scalar_time.count()
           << std::setw(15) << s.vector_time.count()
           << std::setw(10) << std::fixed << std::setprecision(2) << s.speedup << "x\n";
    }

    os << "=================================\n";
}

size_t AlignmentOptimizer::suggestAlignment(size_t element_size, size_t array_size) {
    // Suggest alignment based on SIMD capabilities
    auto features = CPUFeatureDetector::detect();

    if (features.avx512f) return 64;  // AVX-512 uses 64-byte alignment
    if (features.avx || features.avx2) return 32;  // AVX uses 32-byte
    if (features.sse) return 16;  // SSE uses 16-byte

    return element_size;  // Fallback to element size
}

void AlignmentOptimizer::printRecommendations(std::ostream& os) {
    os << "\n=== Alignment Recommendations ===\n";

    auto features = CPUFeatureDetector::detect();

    if (features.avx512f) {
        os << "AVX-512 detected: Use 64-byte alignment (alignas(64))\n";
    } else if (features.avx2) {
        os << "AVX2 detected: Use 32-byte alignment (alignas(32))\n";
    } else if (features.avx) {
        os << "AVX detected: Use 32-byte alignment (alignas(32))\n";
    } else if (features.sse) {
        os << "SSE detected: Use 16-byte alignment (alignas(16))\n";
    } else {
        os << "No SIMD features detected: Standard alignment sufficient\n";
    }

    os << "=================================\n";
}

} // namespace voltron::utility::simd
