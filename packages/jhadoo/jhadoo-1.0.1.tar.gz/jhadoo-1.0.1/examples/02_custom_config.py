"""Custom Configuration - Tailor cleanup to your needs"""

from jhadoo import Config, CleanupEngine
import json

# Create custom config
config_dict = {
    "main_folder": "~/projects",
    "targets": [
        {"name": "venv", "days_threshold": 7, "enabled": True},
        {"name": "node_modules", "days_threshold": 14, "enabled": True},
        {"name": "build", "days_threshold": 14, "enabled": True},
        {"name": "YOUR_CUSTOM_FOLDER", "days_threshold": 7, "enabled": True}
    ],
    "exclusions": ["~/projects/important-project"],
    "safety": {
        "size_threshold_mb": 5000,
        "require_confirmation_above_mb": 500
    }
}

print("Custom Configuration:")
print(json.dumps(config_dict, indent=2))

# Save and use
with open('temp_config.json', 'w') as f:
    json.dump(config_dict, f)

config = Config('temp_config.json')
engine = CleanupEngine(config, dry_run=True)
result = engine.run()

# Cleanup
import os
os.remove('temp_config.json')


