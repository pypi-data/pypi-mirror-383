# jhadoo Examples

Quick, practical examples showing all features.

## Installation
```bash
pip install jhadoo
# OR for local development:
pip install -e .
```

## Examples

### 1. Basic Usage (`01_basic_usage.py`)
Everything you need to get started:
- Dry-run mode (preview)
- Archive mode (safe deletion)
- Actual cleanup

```bash
python examples/01_basic_usage.py
```

### 2. Custom Configuration (`02_custom_config.py`)
Customize cleanup rules:
- Multiple targets
- Custom thresholds
- Exclusions
- Safety settings

```bash
python examples/02_custom_config.py
```

### 3. Scheduling (`03_scheduling.py`)
Automate cleanups:
- Daily/weekly/monthly schedules
- Custom cron expressions
- Manage scheduled tasks

```bash
python examples/03_scheduling.py
```

### Configuration Templates (`config_examples.json`)
Ready-to-use configurations for different scenarios.

## CLI Quick Reference

```bash
# Preview
jhadoo --dry-run

# Run cleanup
jhadoo

# Archive mode
jhadoo --archive

# Schedule daily
jhadoo --schedule daily --archive

# Dashboard
jhadoo --dashboard

# Custom config
jhadoo --config my_config.json
```

## Tips

1. **Always start with `--dry-run`**
2. **Use `--archive` for safety**
3. **Schedule it**: `jhadoo --schedule daily`
4. **Check stats**: `jhadoo --dashboard`
