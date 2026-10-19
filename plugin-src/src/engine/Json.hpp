// Minimal JSON reader for the embedded instrument catalog.
#pragma once

#include <cstdlib>
#include <map>
#include <memory>
#include <string>
#include <vector>

namespace nml {

struct Json {
    enum Type { Null, Bool, Number, String, Array, Object };
    Type type = Null;
    bool b = false;
    double num = 0.0;
    std::string str;
    std::vector<Json> arr;
    std::map<std::string, Json> obj;

    const Json& operator[](const char* key) const {
        static const Json null;
        auto it = obj.find(key);
        return it == obj.end() ? null : it->second;
    }
    const Json& operator[](int i) const {
        static const Json null;
        return (i >= 0 && (size_t)i < arr.size()) ? arr[(size_t)i] : null;
    }
    size_t size() const { return type == Array ? arr.size() : obj.size(); }
    bool has(const char* key) const { return obj.count(key) != 0; }
    int i(int dflt = 0) const { return type == Number ? (int)num : (type == Bool ? (int)b : dflt); }
    double d(double dflt = 0.0) const { return type == Number ? num : dflt; }
    const std::string& s() const { return str; }

    static Json parse(const char* text) {
        const char* p = text;
        Json j = parseValue(p);
        return j;
    }

private:
    static void ws(const char*& p) {
        while (*p == ' ' || *p == '\n' || *p == '\r' || *p == '\t') ++p;
    }
    static Json parseValue(const char*& p) {
        ws(p);
        Json j;
        if (*p == '{') {
            j.type = Object;
            ++p;
            ws(p);
            if (*p == '}') { ++p; return j; }
            for (;;) {
                ws(p);
                std::string key = parseString(p);
                ws(p);
                if (*p == ':') ++p;
                j.obj.emplace(std::move(key), parseValue(p));
                ws(p);
                if (*p == ',') { ++p; continue; }
                if (*p == '}') { ++p; break; }
                break;
            }
        } else if (*p == '[') {
            j.type = Array;
            ++p;
            ws(p);
            if (*p == ']') { ++p; return j; }
            for (;;) {
                j.arr.push_back(parseValue(p));
                ws(p);
                if (*p == ',') { ++p; continue; }
                if (*p == ']') { ++p; break; }
                break;
            }
        } else if (*p == '"') {
            j.type = String;
            j.str = parseString(p);
        } else if (*p == 't') {
            j.type = Bool; j.b = true; p += 4;
        } else if (*p == 'f') {
            j.type = Bool; j.b = false; p += 5;
        } else if (*p == 'n') {
            p += 4;
        } else {
            j.type = Number;
            char* end = nullptr;
            j.num = std::strtod(p, &end);
            p = end ? end : p + 1;
        }
        return j;
    }
    static std::string parseString(const char*& p) {
        std::string out;
        if (*p != '"') return out;
        ++p;
        while (*p && *p != '"') {
            if (*p == '\\') {
                ++p;
                switch (*p) {
                    case 'n': out += '\n'; break;
                    case 't': out += '\t'; break;
                    case 'r': out += '\r'; break;
                    case 'u': {
                        // basic BMP code point -> UTF-8
                        unsigned cp = (unsigned)std::strtoul(std::string(p + 1, 4).c_str(), nullptr, 16);
                        p += 4;
                        if (cp < 0x80) out += (char)cp;
                        else if (cp < 0x800) { out += (char)(0xC0 | (cp >> 6)); out += (char)(0x80 | (cp & 0x3F)); }
                        else { out += (char)(0xE0 | (cp >> 12)); out += (char)(0x80 | ((cp >> 6) & 0x3F)); out += (char)(0x80 | (cp & 0x3F)); }
                        break;
                    }
                    default: out += *p; break;
                }
                ++p;
            } else {
                out += *p++;
            }
        }
        if (*p == '"') ++p;
        return out;
    }
};

}  // namespace nml
