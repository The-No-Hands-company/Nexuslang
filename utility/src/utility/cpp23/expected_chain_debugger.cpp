#include "voltron/utility/cpp23/expected_chain_debugger.h"
#include <iostream>
#include <sstream>

namespace voltron::utility::cpp23 {

// Static member initialization
std::unordered_map<std::string, CoroutineDebugger::CoroutineInfo> CoroutineDebugger::coroutines_;

void CoroutineDebugger::recordSuspend(const std::string& coroutine_name) {
    coroutines_[coroutine_name].name = coroutine_name;
    coroutines_[coroutine_name].suspend_count++;
}

void CoroutineDebugger::recordResume(const std::string& coroutine_name) {
    coroutines_[coroutine_name].name = coroutine_name;
    coroutines_[coroutine_name].resume_count++;
}

void CoroutineDebugger::recordDestroy(const std::string& coroutine_name) {
    coroutines_[coroutine_name].destroyed = true;
}

void CoroutineDebugger::printActiveCoroutines(std::ostream& os) {
    os << "\n=== Active Coroutines ===\n";

    for (const auto& [name, info] : coroutines_) {
        if (!info.destroyed) {
            os << name << ":\n"
               << "  Suspends: " << info.suspend_count << "\n"
               << "  Resumes: " << info.resume_count << "\n";
        }
    }

    os << "=========================\n";
}

void CoroutineDebugger::clear() {
    coroutines_.clear();
}

void ModuleDependencyTracker::registerModule(const std::string& module_name) {
    modules_.insert(module_name);
}

void ModuleDependencyTracker::registerImport(const std::string& from_module,
                                            const std::string& to_module) {
    dependencies_[from_module].push_back(to_module);
}

bool ModuleDependencyTracker::hasCircularDependencies(std::vector<std::string>& cycle_out) const {
    std::unordered_set<std::string> visited;
    std::unordered_set<std::string> rec_stack;

    for (const auto& module : modules_) {
        if (visited.find(module) == visited.end()) {
            if (dfs(module, visited, rec_stack, cycle_out)) {
                return true;
            }
        }
    }

    return false;
}

bool ModuleDependencyTracker::dfs(const std::string& node,
                                 std::unordered_set<std::string>& visited,
                                 std::unordered_set<std::string>& rec_stack,
                                 std::vector<std::string>& cycle) const {
    visited.insert(node);
    rec_stack.insert(node);

    auto it = dependencies_.find(node);
    if (it != dependencies_.end()) {
        for (const auto& neighbor : it->second) {
            if (visited.find(neighbor) == visited.end()) {
                if (dfs(neighbor, visited, rec_stack, cycle)) {
                    cycle.push_back(node);
                    return true;
                }
            } else if (rec_stack.find(neighbor) != rec_stack.end()) {
                // Found cycle
                cycle.push_back(neighbor);
                cycle.push_back(node);
                return true;
            }
        }
    }

    rec_stack.erase(node);
    return false;
}

std::string ModuleDependencyTracker::generateDotGraph() const {
    std::ostringstream oss;

    oss << "digraph ModuleDependencies {\n";
    oss << "  rankdir=LR;\n";

    for (const auto& [from, tos] : dependencies_) {
        for (const auto& to : tos) {
            oss << "  \"" << from << "\" -> \"" << to << "\";\n";
        }
    }

    oss << "}\n";

    return oss.str();
}

void ModuleDependencyTracker::printDependencies(std::ostream& os) const {
    os << "\n=== Module Dependencies ===\n";

    for (const auto& [module, deps] : dependencies_) {
        os << module << " imports:\n";
        for (const auto& dep : deps) {
            os << "  -> " << dep << "\n";
        }
    }

    os << "===========================\n";
}

} // namespace voltron::utility::cpp23
