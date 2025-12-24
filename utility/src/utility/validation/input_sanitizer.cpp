#include "voltron/utility/validation/input_sanitizer.h"
#include <regex>
#include <cmath>
#include <limits>

namespace voltron::utility::validation {

void InputSanitizer::addRule(const std::string& field_name,
                            ValidationRule rule,
                            const std::string& error_message) {
    rules_[field_name].push_back({rule, error_message});
}

bool InputSanitizer::validate(const std::string& field_name,
                             const std::any& value,
                             std::string& error_out) const {
    auto it = rules_.find(field_name);
    if (it == rules_.end()) {
        return true;  // No rules for this field
    }

    for (const auto& rule : it->second) {
        if (!rule.validator(value)) {
            error_out = rule.error_message;
            return false;
        }
    }

    return true;
}

InputSanitizer::ValidationRule InputSanitizer::notEmpty() {
    return [](const std::any& value) -> bool {
        try {
            auto str = std::any_cast<std::string>(value);
            return !str.empty();
        } catch (...) {
            return false;
        }
    };
}

InputSanitizer::ValidationRule InputSanitizer::lengthBetween(size_t min, size_t max) {
    return [min, max](const std::any& value) -> bool {
        try {
            auto str = std::any_cast<std::string>(value);
            return str.length() >= min && str.length() <= max;
        } catch (...) {
            return false;
        }
    };
}

InputSanitizer::ValidationRule InputSanitizer::matchesRegex(const std::string& pattern) {
    return [pattern](const std::any& value) -> bool {
        try {
            auto str = std::any_cast<std::string>(value);
            return std::regex_match(str, std::regex(pattern));
        } catch (...) {
            return false;
        }
    };
}

InputSanitizer::ValidationRule InputSanitizer::isNumeric() {
    return [](const std::any& value) -> bool {
        try {
            auto str = std::any_cast<std::string>(value);
            return std::regex_match(str, std::regex(R"(^-?\d+(\.\d+)?$)"));
        } catch (...) {
            return false;
        }
    };
}

InputSanitizer::ValidationRule InputSanitizer::rangeCheck(double min, double max) {
    return [min, max](const std::any& value) -> bool {
        try {
            double val = std::any_cast<double>(value);
            return val >= min && val <= max;
        } catch (...) {
            return false;
        }
    };
}

bool FloatingPointValidator::isNaN(float value) {
    return std::isnan(value);
}

bool FloatingPointValidator::isNaN(double value) {
    return std::isnan(value);
}

bool FloatingPointValidator::isInf(float value) {
    return std::isinf(value);
}

bool FloatingPointValidator::isInf(double value) {
    return std::isinf(value);
}

bool FloatingPointValidator::isFinite(float value) {
    return std::isfinite(value);
}

bool FloatingPointValidator::isFinite(double value) {
    return std::isfinite(value);
}

bool FloatingPointValidator::approximatelyEqual(float a, float b, float epsilon) {
    return std::fabs(a - b) <= epsilon;
}

bool FloatingPointValidator::approximatelyEqual(double a, double b, double epsilon) {
    return std::fabs(a - b) <= epsilon;
}

bool FloatingPointValidator::validateArray(const float* data, size_t size) {
    for (size_t i = 0; i < size; ++i) {
        if (!isFinite(data[i])) {
            return false;
        }
    }
    return true;
}

bool FloatingPointValidator::validateArray(const double* data, size_t size) {
    for (size_t i = 0; i < size; ++i) {
        if (!isFinite(data[i])) {
            return false;
        }
    }
    return true;
}

} // namespace voltron::utility::validation
