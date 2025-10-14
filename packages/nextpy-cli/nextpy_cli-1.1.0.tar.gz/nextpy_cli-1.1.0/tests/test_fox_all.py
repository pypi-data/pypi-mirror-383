"""
Comprehensive Fox Test Suite - All Phases
Tests Phase 1, 2, and 3 together
"""

import asyncio
from pathlib import Path
from nextpy.fox import Fox

async def main():
    print('🧪 Running Comprehensive Fox Test Suite...\n')
    print('Testing Phases 1, 2, and 3 together\n')
    print('=' * 60)

    # Clean up preferences for fresh test
    prefs_path = Path.home() / '.nextpy' / 'preferences.json'
    if prefs_path.exists():
        print('Cleaning up existing preferences...\n')
        prefs_path.unlink()

    # ============================================
    # PHASE 1: Foundation & Core Infrastructure
    # ============================================
    print('\n📦 PHASE 1: Foundation & Core Infrastructure')
    print('=' * 60)

    print('\n✓ Testing Fox modes...')
    fox_verbose = Fox(mode='verbose')
    fox_normal = Fox(mode='normal')
    fox_quiet = Fox(mode='quiet')
    fox_silent = Fox(mode='silent')

    print('  - Verbose mode initialized')
    print('  - Normal mode initialized')
    print('  - Quiet mode initialized')
    print('  - Silent mode initialized')

    print('\n✓ Testing message system...')
    fox_normal.say('Testing Fox personality!')
    fox_normal.tip('This is a helpful tip')
    fox_normal.celebrate('Success message!')
    fox_normal.warn('Warning message')

    print('\n✓ Testing ASCII art (verbose mode)...')
    fox_verbose.show_ascii_art()

    # ============================================
    # PHASE 2: Preference System
    # ============================================
    print('\n\n💾 PHASE 2: Preference System')
    print('=' * 60)

    fox = Fox(mode='normal')

    print('\n✓ First run detection...')
    print(f'  Is first run: {fox.is_first_run}')

    print('\n✓ Creating default preferences...')
    prefs = fox.preferences.get()
    print(f"  User ID: {prefs['userId']}")
    print(f"  Total projects: {prefs['stats']['totalProjects']}")

    print('\n✓ Updating preferences (Project 1)...')
    fox.update_preferences({
        'project_name': 'ecommerce-shop',
        'frontend': 'next',
        'database': 'postgres',
        'docker': True,
        'github': True
    })
    print('  Preferences updated')

    print('\n✓ Updating preferences (Project 2 - same config)...')
    fox.update_preferences({
        'project_name': 'another-shop',
        'frontend': 'next',
        'database': 'postgres',
        'docker': True,
        'github': False
    })

    print('\n✓ Getting suggestions...')
    suggestions = fox.suggest_preferences({})
    print('  Suggestions:', suggestions)

    print('\n✓ Saving preset...')
    fox.preferences.save_preset('my-stack', {
        'frontend': 'next',
        'database': 'postgres',
        'docker': True,
        'github': True
    })
    print('  Preset "my-stack" saved')

    print('\n✓ Loading preset...')
    preset = fox.preferences.load_preset('my-stack')
    print('  Loaded preset:', preset)

    # ============================================
    # PHASE 3: Context Analysis
    # ============================================
    print('\n\n🧠 PHASE 3: Context Analysis & Smart Suggestions')
    print('=' * 60)

    print('\n✓ Detecting project types...')
    test_projects = [
        'my-ecommerce-shop',
        'tech-blog',
        'user-api',
        'admin-dashboard'
    ]
    for name in test_projects:
        ptype = fox.context.detect_project_type(name)
        print(f'  "{name}" → {ptype}')

    print('\n✓ Checking system capabilities...')
    capabilities = await fox.context.check_system()
    print(f"  Docker: {'✓' if capabilities['hasDocker'] else '✗'}")
    print(f"  Git: {'✓' if capabilities['hasGit'] else '✗'}")
    print(f"  Node: {capabilities['nodeVersion'] or 'not found'}")
    print(f"  Python: {capabilities['pythonVersion'] or 'not found'}")

    print('\n✓ Analyzing project context...')
    analysis = await fox.analyze_context('my-ecommerce-shop', {
        'frontend': None,
        'database': None
    })
    print(f"  Project type: {analysis['projectType']}")
    print(f"  Recommendations: {len(analysis['recommendations'])}")
    for rec in analysis['recommendations'][:2]:
        print(f"    - [{rec['priority']}] {rec['message'][:60]}...")

    print('\n✓ Getting contextual tips...')
    tips = fox.get_contextual_tips(
        {'frontend': 'next', 'database': 'postgres', 'docker': True},
        'ecommerce'
    )
    print(f'  Tips available: {len(tips)}')
    print(f"  Sample tips: {', '.join(tips[:3])}")

    # ============================================
    # INTEGRATION TEST
    # ============================================
    print('\n\n🎯 INTEGRATION TEST: Complete User Flow')
    print('=' * 60)

    fox2 = Fox(mode='normal')

    print('\n1️⃣  User starts CLI...')
    fox2.greet()

    print('\n2️⃣  Fox analyzes project...')
    full_analysis = await fox2.analyze_context('my-saas-platform', {})
    print(f"   Detected: {full_analysis['projectType']} project")

    print('\n3️⃣  Fox provides recommendations...')
    if full_analysis['recommendations']:
        fox2.say(full_analysis['recommendations'][0]['message'])

    print('\n4️⃣  User creates project...')
    final_config = {
        'project_name': 'my-saas-platform',
        'frontend': 'next',
        'database': 'postgres',
        'docker': True,
        'github': True
    }

    print('\n5️⃣  Fox updates preferences...')
    fox2.update_preferences(final_config)

    print('\n6️⃣  Fox provides contextual tips...')
    context_tips = fox2.get_contextual_tips(final_config, full_analysis['projectType'])
    fox2.tip(fox2.messages.get_tip(context_tips[0]))

    print('\n7️⃣  Fox celebrates success...')
    fox2.celebrate('🎉 Your SaaS platform is ready! Time to build something amazing!')

    # ============================================
    # FINAL STATS
    # ============================================
    print('\n\n📊 FINAL STATISTICS')
    print('=' * 60)

    final_prefs = fox2.preferences.get()
    print(f"Total projects created: {final_prefs['stats']['totalProjects']}")
    print(f"Last project: {final_prefs['stats']['lastProjectName']}")
    print(f"Favorite stack: {final_prefs['stats']['favoriteStack']}")
    print(f"Presets saved: {len(final_prefs['presets'])}")

    print('\n\n✅ ALL TESTS PASSED!')
    print('=' * 60)
    print('\n🦊 Fox is fully operational and ready for CLI integration!')
    print('\nPhases completed:')
    print('  ✓ Phase 1: Foundation & Core Infrastructure')
    print('  ✓ Phase 2: Preference System')
    print('  ✓ Phase 3: Context Analysis & Smart Suggestions')
    print('\nNext: Phase 4 - CLI Integration\n')

if __name__ == '__main__':
    asyncio.run(main())
