"""
Smoke test — verify all routers and core modules import cleanly.
Run: python test_smoke.py
"""
import sys
import importlib

ROUTERS = [
    "routers.api_data",
    "routers.api_seo",
    "routers.api_content",
    "routers.api_execution",
    "routers.api_new_features",
    "routers.api_phase2",
    "routers.api_phase3",
    "routers.api_polish",
    "routers.api_serp",
    "routers.api_convert",
]

CORE_MODULES = [
    "core.ab_testing",
    "core.above_fold_analyzer",
    "core.ai_keyword_analyzer",
    "core.article_planner",
    "core.backlink_analyzer",
    "core.competitor_gap_analyzer",
    "core.content_calendar",
    "core.content_length_comparator",
    "core.content_scorer",
    "core.content_scrubber",
    "core.cro_checker",
    "core.cta_analyzer",
    "core.data_aggregator",
    "core.dataforseo",
    "core.engagement_analyzer",
    "core.file_converter",
    "core.ga4_fetcher",
    "core.geo_analyzer",
    "core.google_analytics",
    "core.google_search_console",
    "core.google_serp_scraper",
    "core.keyword_analyzer",
    "core.landing_page_scorer",
    "core.opportunity_scorer",
    "core.rank_tracker",
    "core.readability_scorer",
    "core.report_generator",
    "core.schemas",
    "core.search_intent_analyzer",
    "core.section_writer",
    "core.seo_quality_rater",
    "core.site_manager",
    "core.social_research_aggregator",
    "core.spin_editor",
    "core.technical_seo",
    "core.trust_signal_analyzer",
    "core.wordpress_publisher",
]


def main():
    errors = []
    total = 0

    print("=" * 60)
    print("  AI Marketing Hub — Smoke Test")
    print("=" * 60)

    # Test routers
    print("\n📦 Routers:")
    for mod in ROUTERS:
        total += 1
        try:
            importlib.import_module(mod)
            print(f"  ✅ {mod}")
        except Exception as e:
            print(f"  ❌ {mod}: {e}")
            errors.append((mod, str(e)))

    # Test core modules
    print("\n🧠 Core modules:")
    for mod in CORE_MODULES:
        total += 1
        try:
            importlib.import_module(mod)
            print(f"  ✅ {mod}")
        except Exception as e:
            print(f"  ❌ {mod}: {e}")
            errors.append((mod, str(e)))

    # Test main app
    print("\n🚀 Main app:")
    total += 1
    try:
        import main
        print(f"  ✅ main — {main.app.title} v{main.app.version}")
    except Exception as e:
        print(f"  ❌ main: {e}")
        errors.append(("main", str(e)))

    # Summary
    print("\n" + "=" * 60)
    passed = total - len(errors)
    print(f"  Result: {passed}/{total} passed")
    if errors:
        print(f"  ⚠️  {len(errors)} failures:")
        for mod, err in errors:
            print(f"     • {mod}: {err}")
    else:
        print("  🎉 All imports clean!")
    print("=" * 60)

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
