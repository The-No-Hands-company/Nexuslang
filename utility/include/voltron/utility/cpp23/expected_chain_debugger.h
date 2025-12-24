#pragma once

#include <string>
#include <vector>
#include <expected>

namespace voltron::utility::cpp23 {

/// @brief Debug helper for std::expected
template<typename T, typename E>
class ExpectedChainDebugger {
public:
    using Expected = std::expected<T, E>;

    explicit ExpectedChainDebugger(Expected&& exp)
        : result_(std::move(exp))
    {
        recordOperation("initial", result_.has_value());
    }

    template<typename Func>
    auto andThen(Func&& func) -> ExpectedChainDebugger<std::invoke_result_t<Func, T>::value_type, E> {
        recordOperation("and_then", result_.has_value());

        if (!result_.has_value()) {
            return ExpectedChainDebugger<std::invoke_result_t<Func, T>::value_type, E>(
                std::expected<std::invoke_result_t<Func, T>::value_type, E>(std::unexpect, result_.error()));
        }

        return ExpectedChainDebugger<std::invoke_result_t<Func, T>::value_type, E>(
            func(std::move(*result_)));
    }

    template<typename Func>
    auto orElse(Func&& func) {
        recordOperation("or_else", result_.has_value());

        if (result_.has_value()) {
            return *this;
        }

        return ExpectedChainDebugger(func(std::move(result_.error())));
    }

    void printChain(std::ostream& os) const;

    Expected& get() { return result_; }
    const Expected& get() const { return result_; }

private:
    Expected result_;
    std::vector<std::pair<std::string, bool>> operations_;

    void recordOperation(const std::string& op, bool success);
};

/// @brief Coroutine debugging helper
class CoroutineDebugger {
public:
    static void recordSuspend(const std::string& coroutine_name);
    static void recordResume(const std::string& coroutine_name);
    static void recordDestroy(const std::string& coroutine_name);

    static void printActiveCoroutines(std::ostream& os);
    static void clear();

private:
    struct CoroutineInfo {
        std::string name;
        size_t suspend_count = 0;
        size_t resume_count = 0;
        bool destroyed = false;
    };

    static std::unordered_map<std::string, CoroutineInfo> coroutines_;
};

/// @brief C++ module dependency tracker
class ModuleDependencyTracker {
public:
    void registerModule(const std::string& module_name);
    void registerImport(const std::string& from_module, const std::string& to_module);

    /// Check for circular dependencies
    bool hasCircularDependencies(std::vector<std::string>& cycle_out) const;

    /// Generate dependency graph in DOT format
    std::string generateDotGraph() const;

    void printDependencies(std::ostream& os) const;

private:
    std::set<std::string> modules_;
    std::unordered_map<std::string, std::vector<std::string>> dependencies_;

    bool dfs(const std::string& node,
            std::unordered_set<std::string>& visited,
            std::unordered_set<std::string>& rec_stack,
            std::vector<std::string>& cycle) const;
};

// Template implementations

template<typename T, typename E>
void ExpectedChainDebugger<T, E>::recordOperation(const std::string& op, bool success) {
    operations_.emplace_back(op, success);
}

template<typename T, typename E>
void ExpectedChainDebugger<T, E>::printChain(std::ostream& os) const {
    os << "\n=== Expected Chain Debug ===\n";
    for (const auto& [op, success] : operations_) {
        os << op << ": " << (success ? "value" : "error") << "\n";
    }
    os << "Final result: " << (result_.has_value() ? "value" : "error") << "\n";
    os << "============================\n";
}

} // namespace voltron::utility::cpp23
