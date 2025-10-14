"""
Test Fox Phase 3 - Context Analysis & Smart Suggestions
"""

import asyncio
from nextpy.fox import Fox

async def main():
    print('🧪 Testing Fox Phase 3 - Context Analysis & Smart Suggestions...\n')

    # Test 1: Project Type Detection
    print('=== Test 1: Project Type Detection ===')
    fox = Fox(mode='normal')

    test_projects = [
        'my-ecommerce-shop',
        'tech-blog',
        'user-api',
        'admin-dashboard',
        'saas-platform',
        'personal-portfolio',
        'social-network',
        'booking-system',
        'crypto-wallet',
        'online-academy',
        'random-project'
    ]

    for project_name in test_projects:
        project_type = fox.context.detect_project_type(project_name)
        print(f'"{project_name}" → {project_type}')

    # Test 2: System Capability Detection
    print('\n=== Test 2: System Capability Detection ===')
    capabilities = await fox.context.check_system()
    print('System Capabilities:')
    import json
    print(json.dumps(capabilities, indent=2))

    # Test 3: Database Recommendations
    print('\n=== Test 3: Database Recommendations ===')
    project_types = ['ecommerce', 'blog', 'api', 'dashboard', 'saas', 'finance']
    for ptype in project_types:
        recommendation = fox.context.get_database_recommendation(ptype)
        print(f'\n{ptype}:')
        print(f'  {recommendation or "No specific recommendation"}')

    # Test 4: Frontend Recommendations
    print('\n=== Test 4: Frontend Recommendations ===')
    frontend_types = ['ecommerce', 'blog', 'dashboard', 'portfolio', 'saas']
    for ptype in frontend_types:
        recommendation = fox.context.get_frontend_recommendation(ptype)
        print(f'\n{ptype}:')
        print(f'  {recommendation or "No specific recommendation"}')

    # Test 5: Full Context Analysis
    print('\n=== Test 5: Full Context Analysis ===')
    analysis1 = await fox.analyze_context('my-ecommerce-shop', {
        'frontend': None,
        'database': None,
        'docker': None,
        'github': None
    })

    print('\nProject: my-ecommerce-shop')
    print('Project Type:', analysis1['projectType'])
    print('\nRecommendations:')
    for rec in analysis1['recommendations']:
        print(f"  [{rec['priority']}] {rec['type']}: {rec['message']}")

    # Test 6: Context Analysis with Partial Config
    print('\n=== Test 6: Context Analysis with Partial Config ===')
    analysis2 = await fox.analyze_context('tech-blog', {
        'frontend': 'next',
        'database': None,
        'docker': True,
        'github': False
    })

    print('\nProject: tech-blog (with Next.js, Docker enabled)')
    print('Project Type:', analysis2['projectType'])
    print('\nRecommendations:')
    for rec in analysis2['recommendations']:
        print(f"  [{rec['priority']}] {rec['type']}: {rec['message']}")

    # Test 7: Contextual Tips
    print('\n=== Test 7: Contextual Tips ===')
    config1 = {
        'frontend': 'next',
        'database': 'postgres',
        'docker': True,
        'github': True
    }
    tips1 = fox.get_contextual_tips(config1, 'ecommerce')
    print('\nE-commerce with Next.js + PostgreSQL + Docker + GitHub:')
    print('Tips:', tips1)

    config2 = {
        'frontend': 'vite',
        'database': 'sqlite',
        'docker': False,
        'github': False
    }
    tips2 = fox.get_contextual_tips(config2, 'dashboard')
    print('\nDashboard with Vite + SQLite (no Docker/GitHub):')
    print('Tips:', tips2)

    # Test 8: Show Actual Tip Messages
    print('\n=== Test 8: Actual Tip Messages ===')
    sample_tips = ['postgres_production', 'docker_benefits', 'vite_speed', 'security']
    for tip_key in sample_tips:
        tip_message = fox.messages.get_tip(tip_key)
        print(f'\n{tip_key}:')
        print(f'  💡 {tip_message}')

    # Test 9: Integration Test - Full Flow
    print('\n=== Test 9: Integration Test - Full Flow ===')
    fox2 = Fox(mode='verbose')

    print('\n1. Greeting:')
    fox2.greet()

    print('\n2. Analyzing project context...')
    analysis3 = await fox2.analyze_context('my-saas-platform', {})
    print(f"   Project type detected: {analysis3['projectType']}")

    print('\n3. Recommendations:')
    for rec in analysis3['recommendations']:
        fox2.say(rec['message'])

    print('\n4. Contextual tips:')
    final_config = {
        'frontend': 'next',
        'database': 'postgres',
        'docker': True,
        'github': True
    }
    final_tips = fox2.get_contextual_tips(final_config, analysis3['projectType'])
    for tip_key in final_tips[:3]:  # Show first 3 tips
        fox2.tip(fox2.messages.get_tip(tip_key))

    print('\n5. Celebration:')
    fox2.celebrate('Project analysis complete! Ready to build! 🚀')

    print('\n✅ Phase 3 tests completed!\n')
    print('Fox is now intelligent and context-aware! 🦊🧠')

if __name__ == '__main__':
    asyncio.run(main())
