# 🧹 jhadoo - Universal Cleanup Tool

Smart cleanup for **any** unused files/folders in your projects. Works with Python, Node.js, Rust, Go, Java, C++, or custom folders.

[![PyPI version](https://badge.fury.io/py/jhadoo.svg)](https://badge.fury.io/py/jhadoo)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Quick Start

```bash
# Install
pip install jhadoo

# Preview (safe)
jhadoo --dry-run

# Run cleanup
jhadoo

# Archive mode (safer)
jhadoo --archive

# Schedule daily cleanup
jhadoo --schedule daily --archive

# View stats
jhadoo --dashboard
```

## Features

- **Universal**: Works with ANY file/folder name (venv, node_modules, build, dist, target, or custom)
- **Safe**: Dry-run mode, size caps, confirmations, archive mode
- **Scheduled**: Built-in cron/Task Scheduler integration
- **Cross-platform**: macOS, Windows, Linux
- **Smart**: Dashboard with trends, progress bars, notifications

## Configuration

```bash
# Generate config
jhadoo --generate-config

# Edit and use
jhadoo --config jhadoo_config.json
```

Example config:
```json
{
  "targets": [
    {"name": "venv", "days_threshold": 7, "enabled": true},
    {"name": "node_modules", "days_threshold": 14, "enabled": true},
    {"name": "build", "days_threshold": 14, "enabled": true},
    {"name": "YOUR_CUSTOM_FOLDER", "days_threshold": 7, "enabled": true}
  ],
  "exclusions": ["~/important-project"],
  "safety": {
    "size_threshold_mb": 5000,
    "require_confirmation_above_mb": 500
  }
}
```

## Scheduling

```bash
# Daily at 2 AM
jhadoo --schedule daily

# Weekly (Sunday 2 AM)
jhadoo --schedule weekly

# Custom cron
jhadoo --cron "0 3 * * 1"  # Monday 3 AM

# Manage
jhadoo --list-schedules
jhadoo --remove-schedule
```

## Examples

See [`examples/`](examples/) for detailed code examples:
- **01_basic_usage.py** - Dry-run, archive, actual cleanup
- **02_custom_config.py** - Custom configuration
- **03_scheduling.py** - Automated scheduling

## Universal Support

Works with all languages and build systems:

| Language | Folders |
|----------|---------|
| Python | `venv`, `__pycache__`, `.pytest_cache`, `.tox` |
| Node.js | `node_modules`, `.next`, `.nuxt` |
| Rust | `target` |
| Go | `vendor`, `bin` |
| Java | `target`, `build`, `.gradle` |
| C/C++ | `build`, `*.o` |
| .NET | `bin`, `obj` |
| **Custom** | **Any folder you specify!** |

## Python API

```python
from jhadoo import Config, CleanupEngine, Scheduler

# Run cleanup
config = Config()
engine = CleanupEngine(config, dry_run=True)
result = engine.run()

# Schedule
scheduler = Scheduler()
scheduler.schedule('daily', archive=True)
```

## Command Reference

```
jhadoo [OPTIONS]

Options:
  -c, --config FILE     Custom config file
  -n, --dry-run        Preview without deleting
  -a, --archive        Move to archive instead of delete
  -d, --dashboard      Show statistics
  
  --schedule FREQ     Schedule cleanup (daily/weekly/monthly/hourly)
  --cron EXPR         Custom cron expression
  --list-schedules    List scheduled tasks
  --remove-schedule   Remove scheduled tasks
  
  --generate-config   Create sample config
  -v, --version       Show version
```

## Safety

- **Size warnings**: Alerts if deletion exceeds 5GB
- **Confirmations**: Asks before deleting >500MB  
- **Exclusions**: Protect critical folders
- **System protection**: Never touches OS directories
- **Deletion manifest**: JSON log for recovery

## File Locations

- Logs: `~/.jhadoo/cleanup_log.csv`
- Manifest: `~/.jhadoo/deletion_manifest.json`
- Archive: `~/.jhadoo_archive/`

## License

MIT License - see [LICENSE](LICENSE)

---

**[Examples](examples/) • [Publishing Guide](PUBLISHING.md) • [Technical Docs](jhadoo.md)**