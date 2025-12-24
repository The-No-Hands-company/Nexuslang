#include "voltron/utility/api/contract_validator.h"
#include <iostream>
#include <algorithm>

namespace voltron::utility::api {

void ContractValidator::addPrecondition(Precondition condition) {
    preconditions_.push_back(condition);
}

void ContractValidator::addPostcondition(Postcondition condition) {
    postconditions_.push_back(condition);
}

bool ContractValidator::validatePreconditions(std::vector<std::string>& errors_out) const {
    bool all_valid = true;

    for (const auto& precondition : preconditions_) {
        if (!precondition.check()) {
            errors_out.push_back("Precondition failed: " + precondition.description);
            all_valid = false;
        }
    }

    return all_valid;
}

bool ContractValidator::validatePostconditions(std::vector<std::string>& errors_out) const {
    bool all_valid = true;

    for (const auto& postcondition : postconditions_) {
        if (!postcondition.check()) {
            errors_out.push_back("Postcondition failed: " + postcondition.description);
            all_valid = false;
        }
    }

    return all_valid;
}

void InterfaceValidator::registerInterface(const std::string& interface_name,
                                          const std::vector<MethodSignature>& methods) {
    interfaces_[interface_name] = methods;
}

bool InterfaceValidator::isCompatible(const std::string& interface_name,
                                     const std::vector<MethodSignature>& implementation,
                                     std::vector<std::string>& errors_out) const {
    auto it = interfaces_.find(interface_name);
    if (it == interfaces_.end()) {
        errors_out.push_back("Interface not registered: " + interface_name);
        return false;
    }

    const auto& required_methods = it->second;
    bool compatible = true;

    // Check all required methods are implemented
    for (const auto& required : required_methods) {
        auto found = std::find_if(implementation.begin(), implementation.end(),
            [&required](const MethodSignature& impl) {
                return impl.name == required.name &&
                       impl.parameter_types == required.parameter_types &&
                       impl.return_type == required.return_type;
            });

        if (found == implementation.end()) {
            errors_out.push_back("Missing or incompatible method: " + required.name);
            compatible = false;
        }
    }

    return compatible;
}

void FunctionCallTracer::enterFunction(const std::string& function_name,
                                      const std::vector<std::string>& arguments) {
    call_stack_.push_back({
        function_name,
        arguments,
        std::chrono::steady_clock::now()
    });
}

void FunctionCallTracer::exitFunction(const std::string& function_name,
                                     const std::string& return_value) {
    if (!call_stack_.empty() && call_stack_.back().function_name == function_name) {
        auto duration = std::chrono::steady_clock::now() - call_stack_.back().enter_time;
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(duration).count();

        // Could log duration here
        call_stack_.pop_back();
    }
}

void FunctionCallTracer::printCallStack(std::ostream& os) const {
    os << "\n=== Call Stack ===\n";
    for (size_t i = 0; i < call_stack_.size(); ++i) {
        const auto& frame = call_stack_[i];

        for (size_t j = 0; j < i; ++j) {
            os << "  ";
        }

        os << frame.function_name << "(";
        for (size_t j = 0; j < frame.arguments.size(); ++j) {
            if (j > 0) os << ", ";
            os << frame.arguments[j];
        }
        os << ")\n";
    }
    os << "==================\n";
}

size_t FunctionCallTracer::getStackDepth() const {
    return call_stack_.size();
}

void FunctionCallTracer::clear() {
    call_stack_.clear();
}

} // namespace voltron::utility::api
