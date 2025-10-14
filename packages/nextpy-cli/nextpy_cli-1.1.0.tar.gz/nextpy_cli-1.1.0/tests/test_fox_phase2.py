"""
Test Fox Phase 2 - Preference System
"""

import os
from pathlib import Path
from nextpy.fox import Fox

print('🧪 Testing Fox Phase 2 - Preference System...\n')

# Clean up any existing preferences for testing
prefs_path = Path.home() / '.nextpy' / 'preferences.json'
if prefs_path.exists():
    print('Cleaning up existing preferences...')
    prefs_path.unlink()

# Test 1: First Run Detection
print('=== Test 1: First Run Detection ===')
fox1 = Fox(mode='normal')
print(f'Is first run: {fox1.is_first_run}')
print(f'Preferences exist: {fox1.preferences.exists()}')

# Test 2: Create Default Preferences
print('\n=== Test 2: Create Default Preferences ===')
prefs = fox1.preferences.get()
print('Default preferences created:')
import json
print(json.dumps(prefs, indent=2))

# Test 3: Update Preferences
print('\n=== Test 3: Update Preferences ===')
config1 = {
    'project_name': 'test-project-1',
    'frontend': 'next',
    'database': 'postgres',
    'docker': True,
    'github': False
}

fox1.update_preferences(config1)
print('Preferences updated with config 1')

updated_prefs = fox1.preferences.get()
print('Frontend preference:', updated_prefs['preferences']['frontend'])
print('Database preference:', updated_prefs['preferences']['database'])
print('Total projects:', updated_prefs['stats']['totalProjects'])

# Test 4: Preference Suggestions
print('\n=== Test 4: Preference Suggestions ===')
fox2 = Fox(mode='normal')
print(f'Is first run (second instance): {fox2.is_first_run}')

# Update with same config again to increase count
fox2.update_preferences(config1)
print('Updated preferences again with same config')

suggestions = fox2.suggest_preferences({})
print('Suggestions for new project:', suggestions)

# Test 5: Different Configuration
print('\n=== Test 5: Different Configuration ===')
config2 = {
    'project_name': 'test-project-2',
    'frontend': 'vite',
    'database': 'sqlite',
    'docker': False,
    'github': True
}

fox2.update_preferences(config2)
prefs2 = fox2.preferences.get()
print('Frontend preference after change:', prefs2['preferences']['frontend'])
print('Total projects:', prefs2['stats']['totalProjects'])

# Test 6: Preset System
print('\n=== Test 6: Preset System ===')
fox2.preferences.save_preset('my-saas-stack', {
    'frontend': 'next',
    'database': 'postgres',
    'docker': True,
    'github': True
})
print('Saved preset: my-saas-stack')

presets = fox2.preferences.list_presets()
print('All presets:', presets)

loaded_preset = fox2.preferences.load_preset('my-saas-stack')
print('Loaded preset:', loaded_preset)

# Test 7: Personalized Greeting
print('\n=== Test 7: Personalized Greeting ===')
fox3 = Fox(mode='normal')
fox3.greet()

# Test 8: Milestone Celebration (simulated)
print('\n=== Test 8: Milestone Celebration (simulated) ===')
# Simulate reaching 5 projects
for i in range(3, 6):
    fox3.update_preferences({
        'project_name': f'test-project-{i}',
        'frontend': 'next',
        'database': 'postgres',
        'docker': True,
        'github': False
    })

fox4 = Fox(mode='normal')
fox4.greet()

print('\n✅ Phase 2 tests completed!\n')
print('Check ~/.nextpy/preferences.json to see the stored preferences.')
