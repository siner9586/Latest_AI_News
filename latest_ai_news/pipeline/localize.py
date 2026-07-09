from __future__ import annotations

import hashlib
import html
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from latest_ai_news.config import DATA
from latest_ai_news.pipeline.slugify import stable_slug

CATEGORY_LABELS_ZH = {
    "models-products": "模型与产品",
    "research-open-source": "研究与开源",
    "company-industry": "公司与产业",
    "policy-regulation": "政策与监管",
    "podcasts-interviews": "访谈与播客",
    "funding-startups": "投资与创业",
    "executives": "高管动态",
    "source-index": "来源索引",
}

BANNED_ZH = ("围绕“,", "围绕\"", "围绕“", "出现新动态", "重点：", "Focus:", "new AI-related development around", "key discussion")
BRAND_KEEP = {
    "openai": "OpenAI", "anthropic": "Anthropic", "claude": "Claude", "gemini": "Gemini",
    "grok": "Grok", "nvidia": "NVIDIA", "meta": "Meta", "deepmind": "DeepMind",
    "google": "Google", "microsoft": "Microsoft", "hugging face": "Hugging Face",
    "langchain": "LangChain", "vercel": "Vercel", "mistral": "Mistral", "mufg": "MUFG",
    "together": "Together AI", "modal": "Modal", "swe-bench": "SWE-Bench", "vllm": "vLLM",
}
TERM_MAP = {
    "agent": "能够调用工具、拆解任务并持续执行的 AI 系统。",
    "agents": "能够调用工具、拆解任务并持续执行的 AI 系统。",
    "benchmark": "用于衡量模型能力的任务集合或评测体系。",
    "inference": "模型根据输入生成输出的运行过程，直接影响速度与成本。",
    "throughput": "单位时间内可处理的请求或 token 数，是推理基础设施的重要指标。",
    "sdk": "供开发者集成能力的软件开发工具包。",
    "api": "让开发者通过程序调用模型或平台能力的接口。",
    "open source": "可公开查看、使用或修改的代码与模型资源。",
    "multimodal": "同时处理文本、图像、音频或视频等多种输入输出形式。",
    "coding": "代码生成、修复、评测与软件工程自动化相关能力。",
}


def clean_text(value: str, limit: int | None = None) -> str:
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^(The post|This post)\b.*", "", text, flags=re.I).strip()
    text = re.sub(r"\b(Read more|Continue reading|Listen now|Watch now)\b.*$", "", text, flags=re.I).strip()
    if limit and len(text) > limit:
        return text[:limit].rsplit(" ", 1)[0].strip()
    return text


def is_mostly_english(text: str) -> bool:
    if not text:
        return True
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    alpha = len(re.findall(r"[A-Za-z]", text))
    return alpha > max(18, cjk * 1.8)


def has_bad_template(text: str) -> bool:
    return any(x in str(text or "") for x in BANNED_ZH)


def subject_of(item: dict[str, Any], extracted: dict[str, Any] | None = None) -> str:
    text = " ".join([
        str(item.get("title_original") or item.get("title") or ""),
        str(item.get("summary_en") or item.get("summary") or ""),
        str((extracted or {}).get("extracted_title") or ""),
        " ".join(item.get("tags") or []),
        " ".join(item.get("companies") or []),
    ]).lower()
    for key, label in BRAND_KEEP.items():
        if key in text:
            return label
    names = [*(item.get("companies") or []), *(item.get("people") or [])]
    return str(names[0]) if names else str(item.get("source_name") or "该来源")


def topic_phrase(title: str, excerpt: str, category: str) -> str:
    low = f"{title} {excerpt}".lower()
    if "government" in low or "security" in low or "national" in low:
        return "政府与国家安全合作原则"
    if "educator" in low or "k-12" in low or "academy" in low:
        return "教育场景中的 AI 实用技能培训"
    if "coding" in low or "swe-bench" in low:
        return "代码评测可靠性问题"
    if "voice" in low or "gpt-live" in low:
        return "实时语音交互模型能力"
    if "agent" in low or "harness" in low:
        return "AI 代理工程与工具调用能力"
    if "throughput" in low or "inference" in low:
        return "推理容量与成本控制方案"
    if "benchmark" in low or "evaluation" in low or "research" in low or "paper" in low:
        return "模型评测与研究方法"
    if "funding" in low or "raises" in low or "investment" in low:
        return "融资与资本投入信号"
    if "api" in low or "sdk" in low or "gateway" in low:
        return "开发者接口与平台能力"
    if category == "podcasts-interviews":
        return "行业访谈中的判断与经验"
    if category == "research-open-source":
        return "研究与开源进展"
    if category == "models-products":
        return "模型或产品能力更新"
    return "AI 产业与产品变化"


def action_of(title: str, category: str) -> str:
    low = title.lower()
    if any(x in low for x in ["launch", "introducing", "release", "unveil", "available"]):
        return "发布"
    if any(x in low for x in ["update", "expand", "extend", "support"]):
        return "更新"
    if any(x in low for x in ["benchmark", "evaluat", "achieves"]):
        return "披露"
    if category == "podcasts-interviews":
        return "讨论"
    if category == "funding-startups":
        return "获得"
    return "推进"


def chinese_title(item: dict[str, Any], extracted: dict[str, Any] | None = None) -> str:
    original = clean_text(str((extracted or {}).get("extracted_title") or item.get("title_original") or item.get("title") or ""), 180)
    category = str(item.get("category") or "company-industry")
    subject = subject_of(item, extracted)
    topic = topic_phrase(original, clean_text(str(item.get("summary_en") or item.get("summary") or ""), 240), category)
    action = action_of(original, category)
    title = f"{subject} {action}{topic}"
    title = re.sub(r"\s+", " ", title).strip()
    if len(title) > 38:
        title = title[:36].rstrip("，。；：")
    if len(title) < 8 or is_mostly_english(title):
        title = f"{subject} 发布一项新的 AI 更新"
    return title


def summary_zh(item: dict[str, Any], extracted: dict[str, Any] | None = None) -> str:
    extracted = extracted or {}
    title = str(item.get("title_original") or item.get("title") or "")
    excerpt = clean_text(str(extracted.get("extracted_excerpt") or item.get("summary") or item.get("summary_en") or ""), 260)
    category = str(item.get("category") or "company-industry")
    subject = subject_of(item, extracted)
    topic = topic_phrase(title, excerpt, category)
    if category == "podcasts-interviews":
        text = f"{subject} 的新访谈把焦点放在{topic}，适合观察 AI 产品负责人、创业者和研究者如何判断下一阶段应用边界。"
    elif category == "research-open-source":
        text = f"{subject} 披露了{topic}，对评测指标、开源复现和模型可靠性判断都有参考价值。"
    elif category == "funding-startups":
        text = f"{subject} 释放了{topic}，说明资本仍在寻找可落地的模型、工具链和基础设施机会。"
    elif category == "policy-regulation":
        text = f"{subject} 更新了{topic}，核心影响在于责任边界、合规要求和公共部门采用 AI 的可解释规则。"
    elif category == "models-products":
        text = f"{subject} 更新了{topic}，关键在于模型能力、部署成本、权限控制或开发者工作流的实际变化。"
    else:
        text = f"{subject} 推进了{topic}，需要关注它对 AI 产品落地、企业采用和产业竞争节奏的影响。"
    if excerpt and not is_mostly_english(excerpt) and not has_bad_template(excerpt):
        text = clean_text(excerpt, 120)
    return clean_text(text, 160)


def insight_zh(item: dict[str, Any], extracted: dict[str, Any] | None = None) -> str:
    category = str(item.get("category") or "company-industry")
    subject = subject_of(item, extracted)
    if category == "models-products":
        return f"这条动态的价值不只在发布本身，而在于 {subject} 如何把模型能力转成可部署、可计费、可管理的产品能力。"
    if category == "research-open-source":
        return "它有助于校准对模型能力的判断，尤其适合用于比较评测方法、复现实验与真实应用之间的差距。"
    if category == "podcasts-interviews":
        return "访谈类内容的意义在于暴露一线建设者的真实取舍，可补足正式公告中过于简化的产品叙事。"
    if category == "policy-regulation":
        return "政策与治理信号会改变企业使用 AI 的合规成本，也会影响模型供应商对安全、审计和责任划分的产品设计。"
    return "它提供了观察 AI 产业链变化的一个窗口，尤其适合跟踪企业采用、开发者生态和商业化节奏。"


def key_points_zh(item: dict[str, Any], extracted: dict[str, Any] | None = None) -> list[str]:
    title = str(item.get("title_original") or item.get("title") or "")
    subject = subject_of(item, extracted)
    topic = topic_phrase(title, str(item.get("summary_en") or ""), str(item.get("category") or ""))
    points = [
        f"主体是 {subject}，核心变化集中在{topic}。",
        "原始链接已保留，当前页面只提供中文研究解读与必要证据摘录。",
        "判断价值应放在真实部署、成本、可靠性和生态影响上，而不是只看发布措辞。",
    ]
    tags = item.get("tags") or []
    if tags:
        points.append(f"相关标签包括：{'、'.join(tags[:4])}。")
    if item.get("companies"):
        points.append(f"涉及公司或机构：{'、'.join(item.get('companies', [])[:4])}。")
    return points[:6]


def background_zh(item: dict[str, Any], extracted: dict[str, Any] | None = None) -> str:
    source = item.get("source_name") or "该来源"
    cat = CATEGORY_LABELS_ZH.get(str(item.get("category") or ""), "AI 动态")
    return f"这条内容来自 {source}，归入“{cat}”。中文页基于公开标题、摘要、元数据和可抽取正文生成，不绕过付费墙，也不把不可验证内容包装成事实。"


def impact_zh(item: dict[str, Any], extracted: dict[str, Any] | None = None) -> str:
    category = str(item.get("category") or "company-industry")
    if category == "models-products":
        return "对开发者而言，重点是接口、成本、上下文能力和工具链兼容性；对企业而言，重点是权限、审计、稳定性和实际 ROI。"
    if category == "research-open-source":
        return "对研究者而言，它可作为评测口径和复现实验的参考；对企业部署而言，它提醒不要把单一榜单当作可靠性结论。"
    if category == "podcasts-interviews":
        return "它更适合用作趋势判断材料，而不是单独作为事实依据；关键是和正式公告、产品文档及开源实现交叉验证。"
    if category == "funding-startups":
        return "资本信号会影响人才、算力和生态资源流向，但仍需结合产品留存、客户付费和基础设施成本判断。"
    return "影响主要体现在产品路线、产业竞争、企业采用节奏和开发者生态预期上，需要结合后续真实发布和用户反馈继续观察。"


def terms_zh(item: dict[str, Any], extracted: dict[str, Any] | None = None) -> list[dict[str, str]]:
    text = " ".join([str(item.get("title_original") or item.get("title") or ""), str(item.get("summary_en") or ""), " ".join(item.get("tags") or [])]).lower()
    terms: list[dict[str, str]] = []
    for key, explanation in TERM_MAP.items():
        if key in text and len(terms) < 6:
            term = "AI Agent" if key in {"agent", "agents"} else key.upper() if key in {"api", "sdk"} else key
            terms.append({"term": term, "explanation": explanation})
    return terms


def evidence_zh(item: dict[str, Any], extracted: dict[str, Any] | None = None) -> list[dict[str, str]]:
    evidence = [{"label": "原始来源", "text": clean_text(str(item.get("title_original") or item.get("title") or ""), 160), "source_url": str(item.get("original_url") or "")}]
    excerpt = clean_text(str((extracted or {}).get("extracted_excerpt") or item.get("summary_en") or ""), 220)
    if excerpt:
        evidence.append({"label": "公开摘要", "text": excerpt, "source_url": str(item.get("original_url") or "")})
    return evidence[:3]


def infer_source_license_mode(item: dict[str, Any]) -> str:
    tags = " ".join(item.get("tags") or []).lower()
    source = str(item.get("source_name") or "").lower()
    if "paywall" in tags:
        return "summary_only"
    if any(x in source for x in ["openai", "anthropic", "deepmind", "nvidia", "microsoft", "hugging face", "vercel"]):
        return "official_public"
    return "summary_only"


def content_mode_for(item: dict[str, Any]) -> str:
    if os.getenv("PRIVATE_RESEARCH_MODE", "false").lower() == "true" and item.get("source_license_mode") in {"owned", "allow_full_mirror", "open_license"}:
        return "full_zh_mirror"
    return "research_digest"


def cache_path(item: dict[str, Any], extracted: dict[str, Any]) -> Path:
    h = hashlib.sha1(json.dumps({"url": item.get("original_url"), "title": item.get("title_original") or item.get("title"), "excerpt": extracted.get("extracted_excerpt")}, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    return DATA / "cache" / "localized" / f"{h}.json"


def try_openai_localization(item: dict[str, Any], extracted: dict[str, Any]) -> dict[str, Any] | None:
    if os.getenv("LOCALIZATION_PROVIDER", "rule").lower() != "openai" or not os.getenv("OPENAI_API_KEY"):
        return None
    path = cache_path(item, extracted)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    prompt = {
        "title": item.get("title_original") or item.get("title"),
        "summary": item.get("summary_en") or item.get("summary"),
        "source": item.get("source_name"),
        "category": item.get("category"),
        "excerpt": extracted.get("extracted_excerpt"),
        "text": clean_text(str(extracted.get("extracted_text_for_analysis") or ""), 2200),
    }
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            timeout=30,
            headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}", "Content-Type": "application/json"},
            json={
                "model": os.getenv("LOCALIZATION_OPENAI_MODEL", "gpt-4o-mini"),
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": "你是中文AI情报编辑。输出严格JSON，字段含title_zh, summary_zh, insight_zh, key_points_zh, background_zh, impact_zh, terms_zh, evidence_zh。不得编造事实，不得写围绕/重点/赋能/闭环。"},
                    {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
                ],
            },
        )
        response.raise_for_status()
        data = json.loads(response.json()["choices"][0]["message"]["content"])
        path.parent.mkdir(parents=True, exist_ok=True)
        data["provider"] = "openai"
        data["generated_at"] = datetime.now(timezone.utc).isoformat()
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data
    except Exception:
        return None


def ensure_localized_item(item: dict[str, Any], publish_date: str, extracted: dict[str, Any] | None = None, force: bool = False) -> dict[str, Any]:
    item = dict(item)
    extracted = extracted or {}
    warnings = list(item.get("quality_warnings") or []) + list(extracted.get("quality_warnings") or [])
    item.setdefault("title_original", item.get("title") or extracted.get("extracted_title") or "")
    item.setdefault("title_en", item.get("title_original") or item.get("title") or "")
    item.setdefault("summary_en", clean_text(str(item.get("summary_en") or item.get("summary") or ""), 320))
    item["extracted_title"] = extracted.get("extracted_title", item.get("extracted_title", ""))
    item["extracted_excerpt"] = extracted.get("extracted_excerpt", item.get("extracted_excerpt", ""))
    item["extracted_text_for_analysis"] = extracted.get("extracted_text_for_analysis", item.get("extracted_text_for_analysis", ""))
    item["extraction_status"] = extracted.get("extraction_status") or item.get("extraction_status") or "partial"

    ai = try_openai_localization(item, extracted) if not force else None
    title = (ai or {}).get("title_zh") or item.get("title_zh")
    summary = (ai or {}).get("summary_zh") or item.get("summary_zh")
    if force or not title or is_mostly_english(str(title)):
        title = chinese_title(item, extracted)
    if force or not summary or is_mostly_english(str(summary)) or has_bad_template(str(summary)):
        summary = summary_zh(item, extracted)

    item["title_zh"] = clean_text(str(title), 80)
    item["summary_zh"] = clean_text(str(summary), 180)
    item["insight_zh"] = clean_text(str((ai or {}).get("insight_zh") or item.get("insight_zh") or insight_zh(item, extracted)), 260)
    item["key_points_zh"] = (ai or {}).get("key_points_zh") or item.get("key_points_zh") or key_points_zh(item, extracted)
    item["background_zh"] = clean_text(str((ai or {}).get("background_zh") or item.get("background_zh") or background_zh(item, extracted)), 700)
    item["impact_zh"] = clean_text(str((ai or {}).get("impact_zh") or item.get("impact_zh") or impact_zh(item, extracted)), 700)
    item["terms_zh"] = (ai or {}).get("terms_zh") or item.get("terms_zh") or terms_zh(item, extracted)
    item["evidence_zh"] = (ai or {}).get("evidence_zh") or item.get("evidence_zh") or evidence_zh(item, extracted)
    item["slug"] = item.get("slug") or stable_slug(str(item.get("title_original") or item.get("title_zh") or item.get("title") or ""), str(item.get("original_url") or ""))
    item["localized_url"] = item.get("localized_url") or f"/zh/items/{publish_date}/{item['slug']}/"
    item["source_license_mode"] = item.get("source_license_mode") or infer_source_license_mode(item)
    item["content_mode"] = item.get("content_mode") or content_mode_for(item)
    item["translation_status"] = item.get("translation_status") or ("success" if item.get("title_zh") and item.get("summary_zh") else "fallback")
    item["quality_warnings"] = sorted({w for w in warnings if w})
    item.setdefault("language", "en")
    if item["content_mode"] != "full_zh_mirror":
        item.setdefault("full_text_zh", "")
    return item


def ensure_localized_brief(brief: dict[str, Any], force: bool = False) -> dict[str, Any]:
    publish_date = str(brief.get("date") or datetime.now(timezone.utc).date().isoformat())
    items = [ensure_localized_item(item, publish_date, force=force) for item in brief.get("items", [])]
    brief = dict(brief)
    brief["items"] = items
    brief["selected_count"] = len(items)
    brief["categories"] = sorted({x.get("category") for x in items if x.get("category")})
    return brief
