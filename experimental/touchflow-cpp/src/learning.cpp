#include "learning.hpp"

#include <algorithm>

namespace touchflow {

LearningEngine::LearningEngine(float threshold) : threshold_(threshold) {}

std::string LearningEngine::key(const std::string& app, const std::string& wc) const {
    return app + "|" + wc;
}

float LearningEngine::score(const std::string& app, const std::string& wc) const {
    auto it = patterns_.find(key(app, wc));
    if (it == patterns_.end()) return 0.5f;
    return it->second.score;
}

void LearningEngine::set_score(const std::string& app, const std::string& wc, float s) {
    patterns_[key(app, wc)].score = s;
}

bool LearningEngine::should_auto_show(const std::string& app_id, const std::string& window_class) const {
    return score(app_id, window_class) >= threshold_;
}

void LearningEngine::on_auto_show(const std::string& app_id, const std::string& window_class) {
    auto& p = patterns_[key(app_id, window_class)];
    p.show_count++;
    p.score = std::min(1.0f, p.score + 0.05f);
}

void LearningEngine::on_dismiss(const std::string& app_id, const std::string& window_class, bool immediate) {
    auto& p = patterns_[key(app_id, window_class)];
    p.dismiss_count++;
    if (immediate) p.immediate_count++;
    float penalty = immediate ? 0.15f : 0.08f;
    p.score = std::max(0.0f, p.score - penalty);
}

void LearningEngine::reset() { patterns_.clear(); }

}  // namespace touchflow
