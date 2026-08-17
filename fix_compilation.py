#!/usr/bin/env python3
"""Fix compilation errors in the patched code."""
import sys, os

def patch_file(path, old, new):
    with open(path, 'r') as f:
        content = f.read()
    if old not in content:
        print(f"SKIP: pattern not found in {path}")
        return False
    content = content.replace(old, new, 1)
    with open(path, 'w') as f:
        f.write(content)
    print(f"OK: {path}")
    return True

repo = sys.argv[1] if len(sys.argv) > 1 else '.'

# 1. Fix MusicService.kt: 'datastore' -> 'dataStore' in the new watchers
# The patch added watchers that use 'datastore.data' but correct is 'dataStore.data'
ms_path = f"{repo}/app/src/main/kotlin/com/music/vivi/playback/MusicService.kt"
with open(ms_path, 'r') as f:
    content = f.read()

# Count occurrences of 'datastore' (lowercase) - there should be exactly 2 (in the new watchers)
count = content.count('datastore.')
print(f"Found {count} occurrences of 'datastore.' in MusicService.kt")
if count > 0:
    content = content.replace('datastore.', 'dataStore.')
    with open(ms_path, 'w') as f:
        f.write(content)
    print(f"OK: Fixed {count} occurrences of datastore -> dataStore in MusicService.kt")

# 2. Fix PlayerMenu.kt: add back rememberPreference import
pm_path = f"{repo}/app/src/main/kotlin/com/music/vivi/ui/menu/PlayerMenu.kt"
with open(pm_path, 'r') as f:
    content = f.read()

if 'import com.music.vivi.utils.rememberEnumPreference' in content and 'import com.music.vivi.utils.rememberPreference\n' not in content:
    # Add rememberPreference import after rememberEnumPreference
    content = content.replace(
        'import com.music.vivi.utils.rememberEnumPreference\n',
        'import com.music.vivi.utils.rememberEnumPreference\nimport com.music.vivi.utils.rememberPreference\n'
    )
    with open(pm_path, 'w') as f:
        f.write(content)
    print("OK: Added rememberPreference import to PlayerMenu.kt")
elif 'import com.music.vivi.utils.rememberPreference\n' in content:
    print("SKIP: rememberPreference already imported in PlayerMenu.kt")
else:
    print("WARN: Could not find rememberEnumPreference import in PlayerMenu.kt")

# 3. Fix OldPlayerMenu.kt: same issue if present
opm_path = f"{repo}/app/src/main/kotlin/com/music/vivi/ui/menu/OldPlayerMenu.kt"
if os.path.exists(opm_path):
    with open(opm_path, 'r') as f:
        content = f.read()
    if 'import com.music.vivi.utils.rememberEnumPreference' in content and 'import com.music.vivi.utils.rememberPreference\n' not in content:
        content = content.replace(
            'import com.music.vivi.utils.rememberEnumPreference\n',
            'import com.music.vivi.utils.rememberEnumPreference\nimport com.music.vivi.utils.rememberPreference\n'
        )
        with open(opm_path, 'w') as f:
            f.write(content)
        print("OK: Added rememberPreference import to OldPlayerMenu.kt")
    else:
        print("SKIP: OldPlayerMenu.kt already has rememberPreference or doesn't use rememberEnumPreference")

# 4. Fix JioSettings.kt: same issue if present
js_path = f"{repo}/app/src/main/kotlin/com/music/vivi/ui/screens/settings/JioSettings.kt"
if os.path.exists(js_path):
    with open(js_path, 'r') as f:
        content = f.read()
    if 'import com.music.vivi.utils.rememberEnumPreference' in content and 'import com.music.vivi.utils.rememberPreference\n' not in content:
        content = content.replace(
            'import com.music.vivi.utils.rememberEnumPreference\n',
            'import com.music.vivi.utils.rememberEnumPreference\nimport com.music.vivi.utils.rememberPreference\n'
        )
        with open(ps_path, 'w') as f:
            f.write(content)
        print("OK: Added rememberPreference import to JioSettings.kt")
    else:
        print("SKIP: JioSettings.kt already has rememberPreference or doesn't use rememberEnumPreference")

# 5. Fix PlayerSettings.kt: same issue if present
ps_path = f"{repo}/app/src/main/kotlin/com/music/vivi/ui/screens/settings/PlayerSettings.kt"
if os.path.exists(ps_path):
    with open(ps_path, 'r') as f:
        content = f.read()
    if 'import com.music.vivi.utils.rememberEnumPreference' in content and 'import com.music.vivi.utils.rememberPreference\n' not in content:
        content = content.replace(
            'import com.music.vivi.utils.rememberEnumPreference\n',
            'import com.music.vivi.utils.rememberEnumPreference\nimport com.music.vivi.utils.rememberPreference\n'
        )
        with open(ps_path, 'w') as f:
            f.write(content)
        print("OK: Added rememberPreference import to PlayerSettings.kt")
    else:
        print("SKIP: PlayerSettings.kt already has rememberPreference or doesn't use rememberEnumPreference")

print("\nDone! Compilation fixes applied.")
