#!/usr/bin/env python3

"""Test script for Fox functionality in Python CLI"""

import sys
import asyncio
from nextpy.fox import Fox

async def test_fox():
    print('🧪 Testing Fox in Python CLI\n')
    print('=' * 50)
    
    try:
        # Test 1: Initialize Fox
        print('\n✅ Test 1: Initialize Fox')
        fox = Fox(mode='verbose')
        print('   Fox initialized successfully')
        
        # Test 2: Greet
        print('\n✅ Test 2: Fox Greeting')
        fox.greet()
        
        # Test 3: Say message
        print('\n✅ Test 3: Fox Say')
        backend_msg = fox.messages.get_progress('backend')
        fox.say(backend_msg)
        
        # Test 4: Tip
        print('\n✅ Test 4: Fox Tip')
        docker_tip = fox.messages.get_tip('docker_benefits')
        fox.tip(docker_tip)
        
        # Test 5: Celebrate
        print('\n✅ Test 5: Fox Celebrate')
        success_msg = fox.messages.get_success()
        fox.celebrate(success_msg)
        
        # Test 6: Preferences
        print('\n✅ Test 6: Preferences')
        prefs = fox.preferences.get()
        print(f'   Preferences loaded: totalProjects={prefs["stats"]["totalProjects"]}, foxMode={prefs["foxMode"]}')
        
        # Test 7: Context Analysis
        print('\n✅ Test 7: Context Analysis')
        context = await fox.context.analyze('my-ecommerce-shop', {})
        print(f'   Project type detected: {context["projectType"]}')
        print(f'   System capabilities: {context["systemCapabilities"]}')
        
        # Test 8: Preference Suggestions
        print('\n✅ Test 8: Preference Suggestions')
        suggestions = fox.suggest_preferences({'projectName': 'test-app'})
        print(f'   Suggestions: {suggestions}')
        
        # Test 9: Different modes
        print('\n✅ Test 9: Different Modes')
        modes = ['normal', 'quiet', 'silent']
        for mode in modes:
            test_fox = Fox(mode=mode)
            print(f'   Mode: {mode}')
            msg = test_fox.messages.get_success()
            test_fox.say(msg)
        
        print('\n' + '=' * 50)
        print('🎉 All tests passed! Fox is working correctly.\n')
        
    except Exception as error:
        print(f'\n❌ Test failed: {str(error)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(test_fox())
