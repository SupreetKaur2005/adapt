import sys
sys.path.insert(0, r"d:\adapt\src")
from adapt.sandbox.telemetry_producers import live_stream
events = list(live_stream())
print("live_stream events:", len(events))
for e in events:
    print(" -", e)