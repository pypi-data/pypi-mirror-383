"""Scheduling - Automate your cleanups"""

from jhadoo import Scheduler

scheduler = Scheduler()

print("Scheduling Examples")
print("="*60)

# Examples (uncomment to use)
print("\n1. Daily cleanup at 2 AM:")
print("   scheduler.schedule('daily', archive=True)")

print("\n2. Weekly cleanup (Sunday 2 AM):")
print("   scheduler.schedule('weekly', archive=True)")

print("\n3. Custom schedule (Monday 3 AM):")
print("   scheduler.schedule('0 3 * * 1', archive=True)")

print("\n4. With custom config:")
print("   scheduler.schedule('daily', config_path='my_config.json')")

print("\n" + "="*60)
print("Management:")
print("  scheduler.list_schedules()    # Show scheduled tasks")
print("  scheduler.remove_schedule()   # Remove all schedules")

# Uncomment to actually schedule:
# scheduler.schedule('daily', archive=True)
# scheduler.list_schedules()