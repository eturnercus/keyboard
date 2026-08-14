#pragma once

#include <string>
#include <map>

namespace touchflow {

class LearningEngine {
public:
    explicit LearningEngine(float threshold = 0.35f);
    bool should_auto_show(const std::string& app_id, const std::string& window_class) const;
    void on_auto_show(const std::string& app_id, const std::string& window_class);
    void on_dismiss(const std::string& app_id, const std::string& window_class, bool immediate);
    void reset();

private:
    struct Pattern {
        int show_count{0};
        int dismiss_count{0};
        int immediate_count{0};
        float score{0.5f};
    };
    float threshold_;
    std::map<std::string, Pattern> patterns_;
    std::string key(const std::string& app, const std::string& wc) const;
    float score(const std::string& app, const std::string& wc) const;
    void set_score(const std::string& app, const std::string& wc, float s);
};

}  // namespace touchflow
