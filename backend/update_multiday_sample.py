import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.gigs.models import Gigs, GigsLineup

# 1. Big Bang Festival 2026 (ID 240) - 3 Hari
bigbang = Gigs.objects.filter(id=240).first()
if bigbang:
    lineups = list(bigbang.lineups.all().order_by('id'))
    print(f"Big Bang has {len(lineups)} artists")
    
    # Day 1 (4 artists)
    # Day 2 (4 artists)
    # Day 3 (2 artists)
    schedule = [
        ("Day 1", "16:30 WIB"),
        ("Day 1", "18:15 WIB"),
        ("Day 1", "20:00 WIB"),
        ("Day 1", "21:30 WIB"),
        ("Day 2", "16:00 WIB"),
        ("Day 2", "17:45 WIB"),
        ("Day 2", "19:30 WIB"),
        ("Day 2", "21:15 WIB"),
        ("Day 3", "17:00 WIB"),
        ("Day 3", "19:00 WIB"),
    ]
    for idx, l in enumerate(lineups):
        day, stime = schedule[idx] if idx < len(schedule) else ("Day 3", "20:30 WIB")
        l.day = day
        l.set_time = stime
        l.order = idx + 1
        l.save()
        print(f"  [order={l.order}] [{l.day}] {l.artist.name} -> {l.set_time}")

# 2. Remember Fest 2026 (ID 239) - 2 Hari
rem = Gigs.objects.filter(id=239).first()
if rem:
    r_lineups = list(rem.lineups.all().order_by('id'))
    print(f"Remember Fest has {len(r_lineups)} artists")
    
    half = len(r_lineups) // 2  # 15 for Day 1, 16 for Day 2
    
    day1_times = [
        "14:00 WIB", "14:35 WIB", "15:10 WIB", "15:45 WIB", "16:20 WIB",
        "17:00 WIB", "17:40 WIB", "18:20 WIB", "19:00 WIB", "19:40 WIB",
        "20:20 WIB", "21:00 WIB", "21:40 WIB", "22:20 WIB", "23:00 WIB"
    ]
    day2_times = [
        "14:00 WIB", "14:35 WIB", "15:10 WIB", "15:45 WIB", "16:20 WIB",
        "17:00 WIB", "17:40 WIB", "18:20 WIB", "19:00 WIB", "19:40 WIB",
        "20:20 WIB", "21:00 WIB", "21:40 WIB", "22:20 WIB", "23:00 WIB", "23:45 WIB"
    ]
    
    for idx, l in enumerate(r_lineups):
        if idx < half:
            l.day = "Day 1"
            l.set_time = day1_times[idx] if idx < len(day1_times) else "22:00 WIB"
        else:
            d2_idx = idx - half
            l.day = "Day 2"
            l.set_time = day2_times[d2_idx] if d2_idx < len(day2_times) else "22:30 WIB"
        l.order = idx + 1
        l.save()
        print(f"  [order={l.order}] [{l.day}] {l.artist.name} -> {l.set_time}")

print("Multi-day lineup assignments updated and ordered sequentially!")
