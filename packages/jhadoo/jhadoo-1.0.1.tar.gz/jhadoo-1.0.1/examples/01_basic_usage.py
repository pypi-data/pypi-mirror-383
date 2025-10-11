"""Basic Usage - All common scenarios in one example"""

from jhadoo import Config, CleanupEngine

print("="*60)
print("jhadoo - Basic Usage Examples")
print("="*60)

# 1. Dry Run (Preview - SAFE, no actual deletion)
print("\n1. DRY RUN MODE (Preview)")
config = Config()
engine = CleanupEngine(config, dry_run=True)
result = engine.run()
print(f"→ Would delete: {result['stats']['folders_deleted']} items")

# 2. Archive Mode (Move instead of delete)
print("\n2. ARCHIVE MODE (Safe)")
engine = CleanupEngine(config, archive_mode=True, dry_run=True)
result = engine.run()
print(f"→ Files would be moved to archive, not deleted")

# 3. Actual Cleanup (USE WITH CAUTION)
print("\n3. ACTUAL CLEANUP")
print("→ Uncomment below to run actual cleanup:")
# engine = CleanupEngine(config, dry_run=False)
# result = engine.run()

print("\n" + "="*60)
print("💡 Pro Tips:")
print("  • Always test with dry_run=True first")
print("  • Use archive_mode=True for safer deletion")
print("  • Check dashboard: jhadoo --dashboard")
