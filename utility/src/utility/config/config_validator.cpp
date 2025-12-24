#include "voltron/utility/config/config_validator.h"
#include <iostream>
#include <fstream>
#include <cstdlib>

namespace voltron::utility::config {

void ConfigValidator::addRule(const std::string& key, const Rule& rule) {
    rules_[key] = rule;
}

bool ConfigValidator::validate(const std::unordered_map<std::string, std::any>& config,
                              std::vector<std::string>& errors_out) const {
    bool valid = true;

    // Check all rules
    for (const auto& [key, rule] : rules_) {
        auto it = config.find(key);

        if (it == config.end()) {
            if (rule.required) {
                errors_out.push_back("Missing required key: " + key);
                valid = false;
            }
            continue;
        }

        // Type validation would go here
        // In real implementation, check std::any type matches expected_type
    }

    return valid;
}

void ConfigValidator::printSchema(std::ostream& os) const {
    os << "\n=== Configuration Schema ===\n";
    for (const auto& [key, rule] : rules_) {
        os << key << " (" << (rule.required ? "required" : "optional") << ")\n";
        os << "  Type: ";

        switch (rule.expected_type) {
            case ValueType::String: os << "string"; break;
            case ValueType::Integer: os << "integer"; break;
            case ValueType::Float: os << "float"; break;
            case ValueType::Boolean: os << "boolean"; break;
            case ValueType::Array: os << "array"; break;
            case ValueType::Object: os << "object"; break;
        }

        os << "\n";
        if (!rule.description.empty()) {
            os << "  Description: " << rule.description << "\n";
        }
    }
    os << "============================\n";
}

std::string EnvironmentReader::get(const std::string& var_name,
                                   const std::string& default_value) {
    const char* value = std::getenv(var_name.c_str());
    return value ? std::string(value) : default_value;
}

int EnvironmentReader::getInt(const std::string& var_name, int default_value) {
    std::string value = get(var_name);
    if (value.empty()) {
        return default_value;
    }

    try {
        return std::stoi(value);
    } catch (...) {
        return default_value;
    }
}

bool EnvironmentReader::getBool(const std::string& var_name, bool default_value) {
    std::string value = get(var_name);
    if (value.empty()) {
        return default_value;
    }

    // Check common boolean representations
    if (value == "1" || value == "true" || value == "TRUE" || value == "yes" || value == "YES") {
        return true;
    }
    if (value == "0" || value == "false" || value == "FALSE" || value == "no" || value == "NO") {
        return false;
    }

    return default_value;
}

double EnvironmentReader::getDouble(const std::string& var_name, double default_value) {
    std::string value = get(var_name);
    if (value.empty()) {
        return default_value;
    }

    try {
        return std::stod(value);
    } catch (...) {
        return default_value;
    }
}

bool EnvironmentReader::exists(const std::string& var_name) {
    return std::getenv(var_name.c_str()) != nullptr;
}

bool EnvironmentReader::set(const std::string& var_name, const std::string& value) {
#ifdef _WIN32
    return _putenv_s(var_name.c_str(), value.c_str()) == 0;
#else
    return setenv(var_name.c_str(), value.c_str(), 1) == 0;
#endif
}

std::vector<std::pair<std::string, std::string>> EnvironmentReader::listAll() {
    std::vector<std::pair<std::string, std::string>> vars;

#ifdef _WIN32
    // Windows implementation would use _environ
#else
    extern char** environ;
    for (char** env = environ; *env != nullptr; ++env) {
        std::string entry(*env);
        size_t pos = entry.find('=');
        if (pos != std::string::npos) {
            vars.emplace_back(entry.substr(0, pos), entry.substr(pos + 1));
        }
    }
#endif

    return vars;
}

void RuntimeConfig::set(const std::string& key, const std::any& value) {
    config_[key] = value;
}

bool RuntimeConfig::has(const std::string& key) const {
    return config_.find(key) != config_.end();
}

void RuntimeConfig::remove(const std::string& key) {
    config_.erase(key);
}

void RuntimeConfig::loadFromFile(const std::string& filename) {
    // Simplified implementation - production would use JSON/YAML parser
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open config file: " + filename);
    }

    // Simple key=value parser
    std::string line;
    while (std::getline(file, line)) {
        if (line.empty() || line[0] == '#') continue;

        size_t pos = line.find('=');
        if (pos != std::string::npos) {
            std::string key = line.substr(0, pos);
            std::string value = line.substr(pos + 1);
            config_[key] = value;
        }
    }
}

void RuntimeConfig::saveToFile(const std::string& filename) const {
    std::ofstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open config file for writing: " + filename);
    }

    for (const auto& [key, value] : config_) {
        // Simplified - production would properly serialize std::any
        file << key << "=[value]\n";
    }
}

void RuntimeConfig::printAll(std::ostream& os) const {
    os << "\n=== Runtime Configuration ===\n";
    for (const auto& [key, value] : config_) {
        os << key << " = [value]\n";
    }
    os << "=============================\n";
}

} // namespace voltron::utility::config
