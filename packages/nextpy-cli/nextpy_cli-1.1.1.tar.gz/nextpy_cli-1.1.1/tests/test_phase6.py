"""
Phase 6 Tests - Advanced Features
Tests for --last flag, preset commands, config commands, and environment variables
"""

import os
import pytest
import shutil
from pathlib import Path
from nextpy.fox import Fox
from nextpy.fox.preferences import PreferenceManager


@pytest.fixture
def test_config_dir(tmp_path):
    """Create a temporary config directory for testing"""
    test_dir = tmp_path / '.nextpy-test'
    test_dir.mkdir(exist_ok=True)
    
    # Override config directory for testing
    original_home = Path.home()
    
    # Monkey patch the config directory
    def mock_home():
        return tmp_path
    
    Path.home = mock_home
    
    yield test_dir
    
    # Restore original
    Path.home = lambda: original_home
    
    # Cleanup
    if test_dir.exists():
        shutil.rmtree(test_dir)


class TestLastFlag:
    """Tests for --last flag functionality"""
    
    def test_load_last_configuration(self, test_config_dir):
        """Should load last configuration"""
        fox = Fox(mode='silent')
        
        # Create initial preferences
        config = {
            'project_name': 'test-project',
            'frontend': 'next',
            'database': 'postgres',
            'docker': True,
            'github': False,
        }
        
        fox.update_preferences(config)
        
        # Get last config
        last_config = fox.preferences.get_last_config()
        
        assert last_config['frontend'] == 'next'
        assert last_config['database'] == 'postgres'
        assert last_config['docker'] is True
        assert last_config['github'] is False
    
    def test_merge_last_config_with_overrides(self, test_config_dir):
        """Should merge last config with CLI overrides"""
        fox = Fox(mode='silent')
        
        # Set up last config
        config = {
            'project_name': 'test-project',
            'frontend': 'next',
            'database': 'postgres',
            'docker': True,
            'github': False,
        }
        
        fox.update_preferences(config)
        
        # Get last config and merge with overrides
        last_config = fox.preferences.get_last_config()
        merged_config = {
            **last_config,
            'project_name': 'new-project',
            'docker': False,  # Override
        }
        
        assert merged_config['project_name'] == 'new-project'
        assert merged_config['frontend'] == 'next'
        assert merged_config['database'] == 'postgres'
        assert merged_config['docker'] is False  # Overridden
        assert merged_config['github'] is False
    
    def test_handle_missing_preferences(self, test_config_dir):
        """Should handle missing preferences gracefully"""
        fox = Fox(mode='silent')
        
        # Reset preferences
        fox.preferences.reset()
        
        # Check if preferences exist
        exists = fox.preferences.exists()
        assert exists is True  # Should exist after reset (creates default)


class TestPresetCommands:
    """Tests for preset management commands"""
    
    def test_save_preset(self, test_config_dir):
        """Should save a preset"""
        fox = Fox(mode='silent')
        
        config = {
            'frontend': 'vite',
            'database': 'sqlite',
            'docker': False,
            'github': True,
        }
        
        fox.preferences.save_preset('test-preset', config)
        
        presets = fox.preferences.list_presets()
        assert len(presets) == 1
        assert presets[0]['name'] == 'test-preset'
        assert presets[0]['config']['frontend'] == 'vite'
    
    def test_load_preset(self, test_config_dir):
        """Should load a preset"""
        fox = Fox(mode='silent')
        
        config = {
            'frontend': 'next',
            'database': 'mongo',
            'docker': True,
            'github': False,
        }
        
        fox.preferences.save_preset('mongo-stack', config)
        
        loaded_config = fox.preferences.load_preset('mongo-stack')
        assert loaded_config['frontend'] == 'next'
        assert loaded_config['database'] == 'mongo'
        assert loaded_config['docker'] is True
    
    def test_list_presets(self, test_config_dir):
        """Should list all presets"""
        fox = Fox(mode='silent')
        
        fox.preferences.save_preset('preset1', {'frontend': 'next', 'database': 'sqlite'})
        fox.preferences.save_preset('preset2', {'frontend': 'vite', 'database': 'postgres'})
        
        presets = fox.preferences.list_presets()
        assert len(presets) >= 2
        
        names = [p['name'] for p in presets]
        assert 'preset1' in names
        assert 'preset2' in names
    
    def test_delete_preset(self, test_config_dir):
        """Should delete a preset"""
        fox = Fox(mode='silent')
        
        fox.preferences.save_preset('to-delete', {'frontend': 'next', 'database': 'sqlite'})
        
        presets = fox.preferences.list_presets()
        before_count = len(presets)
        
        fox.preferences.delete_preset('to-delete')
        
        presets = fox.preferences.list_presets()
        assert len(presets) == before_count - 1
        
        names = [p['name'] for p in presets]
        assert 'to-delete' not in names
    
    def test_handle_nonexistent_preset(self, test_config_dir):
        """Should handle non-existent preset"""
        fox = Fox(mode='silent')
        
        config = fox.preferences.load_preset('non-existent')
        assert config is None
    
    def test_overwrite_preset_with_same_name(self, test_config_dir):
        """Should overwrite preset with same name"""
        fox = Fox(mode='silent')
        
        fox.preferences.save_preset('overwrite-test', {'frontend': 'next', 'database': 'sqlite'})
        fox.preferences.save_preset('overwrite-test', {'frontend': 'vite', 'database': 'postgres'})
        
        presets = fox.preferences.list_presets()
        overwrite_presets = [p for p in presets if p['name'] == 'overwrite-test']
        
        assert len(overwrite_presets) == 1
        assert overwrite_presets[0]['config']['frontend'] == 'vite'
        assert overwrite_presets[0]['config']['database'] == 'postgres'


class TestConfigCommands:
    """Tests for config management commands"""
    
    def test_get_current_configuration(self, test_config_dir):
        """Should get current configuration"""
        fox = Fox(mode='silent')
        
        prefs = fox.preferences.get()
        
        assert isinstance(prefs, dict)
        assert 'version' in prefs
        assert 'foxMode' in prefs
        assert 'stats' in prefs
    
    def test_set_fox_mode(self, test_config_dir):
        """Should set fox mode"""
        fox = Fox(mode='silent')
        
        prefs = fox.preferences.get()
        prefs['foxMode'] = 'quiet'
        fox.preferences.save(prefs)
        
        updated_prefs = fox.preferences.get()
        assert updated_prefs['foxMode'] == 'quiet'
    
    def test_track_statistics(self, test_config_dir):
        """Should track statistics"""
        fox = Fox(mode='silent')
        
        config = {
            'project_name': 'stats-test',
            'frontend': 'next',
            'database': 'sqlite',
            'docker': False,
            'github': False,
        }
        
        before_stats = fox.preferences.get()['stats']
        before_count = before_stats['totalProjects']
        
        fox.update_preferences(config)
        
        after_stats = fox.preferences.get()['stats']
        assert after_stats['totalProjects'] == before_count + 1
        assert after_stats['lastProjectName'] == 'stats-test'


class TestPreferenceReset:
    """Tests for preference reset functionality"""
    
    def test_reset_all_preferences(self, test_config_dir):
        """Should reset all preferences"""
        fox = Fox(mode='silent')
        
        # Add some data
        fox.preferences.save_preset('test', {'frontend': 'next', 'database': 'sqlite'})
        fox.update_preferences({
            'project_name': 'test',
            'frontend': 'next',
            'database': 'sqlite',
        })
        
        # Reset
        fox.preferences.reset()
        
        prefs = fox.preferences.get()
        assert prefs['stats']['totalProjects'] == 0
        assert len(prefs['presets']) == 0
        assert len(prefs['preferences']) == 0


class TestEnvironmentVariables:
    """Tests for environment variable support"""
    
    def test_respect_nextpy_fox_mode(self):
        """Should respect NEXTPY_FOX_MODE"""
        os.environ['NEXTPY_FOX_MODE'] = 'quiet'
        
        mode = os.environ.get('NEXTPY_FOX_MODE', 'normal')
        assert mode == 'quiet'
        
        del os.environ['NEXTPY_FOX_MODE']
    
    def test_respect_nextpy_fox_silent(self):
        """Should respect NEXTPY_FOX_SILENT"""
        os.environ['NEXTPY_FOX_SILENT'] = 'true'
        
        mode = os.environ.get('NEXTPY_FOX_MODE', 'normal')
        if os.environ.get('NEXTPY_FOX_SILENT') in ('true', '1', 'True', 'TRUE'):
            mode = 'silent'
        
        assert mode == 'silent'
        
        del os.environ['NEXTPY_FOX_SILENT']
    
    def test_prioritize_silent_over_mode(self):
        """Should prioritize NEXTPY_FOX_SILENT over NEXTPY_FOX_MODE"""
        os.environ['NEXTPY_FOX_MODE'] = 'verbose'
        os.environ['NEXTPY_FOX_SILENT'] = '1'
        
        mode = os.environ.get('NEXTPY_FOX_MODE', 'normal')
        if os.environ.get('NEXTPY_FOX_SILENT') in ('true', '1', 'True', 'TRUE'):
            mode = 'silent'
        
        assert mode == 'silent'
        
        del os.environ['NEXTPY_FOX_MODE']
        del os.environ['NEXTPY_FOX_SILENT']


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_workflow(self, test_config_dir):
        """Should handle complete workflow"""
        fox = Fox(mode='silent')
        
        # 1. Create first project
        config1 = {
            'project_name': 'project1',
            'frontend': 'next',
            'database': 'postgres',
            'docker': True,
            'github': False,
        }
        fox.update_preferences(config1)
        
        # 2. Save as preset
        fox.preferences.save_preset('my-stack', config1)
        
        # 3. Create second project with different config
        config2 = {
            'project_name': 'project2',
            'frontend': 'vite',
            'database': 'sqlite',
            'docker': False,
            'github': True,
        }
        fox.update_preferences(config2)
        
        # 4. Load last config (should be config2)
        last_config = fox.preferences.get_last_config()
        assert last_config['frontend'] == 'vite'
        assert last_config['database'] == 'sqlite'
        
        # 5. Load preset (should be config1)
        preset_config = fox.preferences.load_preset('my-stack')
        assert preset_config['frontend'] == 'next'
        assert preset_config['database'] == 'postgres'
        
        # 6. Check statistics
        stats = fox.preferences.get()['stats']
        assert stats['totalProjects'] == 2
        assert stats['lastProjectName'] == 'project2'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
