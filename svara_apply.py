#!/usr/bin/env python3
"""
Svara modification script — runs inside GitHub Actions.
v3: Fixed all three user complaints:
  - JioSaavn as primary stream (EnableSaavnStreamingKey default true)
  - App drawer shows "Svara" not "Svara Debug"
  - Downloads copied to public Downloads/Svara/ folder
"""
import os, sys, glob, re

def fix(path, replacements):
    """Apply text replacements to a file if it exists."""
    if not os.path.exists(path):
        return 0
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    orig = c
    n = 0
    for old, new in replacements:
        if old in c:
            c = c.replace(old, new)
            n += 1
    if c != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"  OK: {os.path.relpath(path)} ({n} replacements)")
        return 1
    return 0

def fix_xml_text_only(path, replacements):
    """Replace text only inside >text< content, NOT inside name="..." attributes.
    This prevents breaking R.string resource key references."""
    if not os.path.exists(path):
        return 0
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    orig = c
    n = 0
    lines = c.split('\n')
    new_lines = []
    for line in lines:
        new_line = line
        def replace_text(m):
            nonlocal n
            text = m.group(1)
            for old, new in replacements:
                if old in text:
                    text = text.replace(old, new)
                    n += 1
            return '>' + text + '<'
        new_line = re.sub(r'>([^<]*)<', replace_text, new_line)
        new_lines.append(new_line)
    c = '\n'.join(new_lines)
    if c != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"  OK: {os.path.relpath(path)} ({n} text replacements)")
        return 1
    return 0

repo = sys.argv[1] if len(sys.argv) > 1 else '.'
changed = 0

# ════════════════════════════════════════════════════════════════
# 1. REBRAND: Vivi Music -> Svara, VIVIDH P ASHOKAN -> YASH AGRAWAL
# ════════════════════════════════════════════════════════════════
print("=== REBRAND ===")

# app_name.xml (main) -> "Svara"
changed += fix(f'{repo}/app/src/main/res/values/app_name.xml', [
    ('>VIVI<', '>Svara<'),
])

# app_name.xml (debug) -> "Svara" (NOT "Svara Debug")
# This fixes the app drawer showing "Svara Debug"
changed += fix(f'{repo}/app/src/debug/res/values/app_name.xml', [
    ('>VIVI Debug<', '>Svara<'),
    ('>Svara Debug<', '>Svara<'),
])

# updater_strings.xml
changed += fix(f'{repo}/app/src/main/res/values/updater_strings.xml', [
    ('>VIVI MUSIC version', '>Svara version'),
    ('>VIVI MUSIC<', '>SVARA<'),
    ('>VIVIDH P ASHOKAN<', '>YASH AGRAWAL<'),
    ('vivi-music %1$s', 'Svara %1$s'),
    ('vivi-music', 'Svara'),
])
for f in glob.glob(f'{repo}/app/src/main/res/values-*/updater_strings.xml'):
    changed += fix_xml_text_only(f, [
        ('VIVI MUSIC', 'SVARA'),
        ('VIVIDH P ASHOKAN', 'YASH AGRAWAL'),
        ('vivi-music', 'Svara'),
        ('Vivi Music', 'Svara'),
        ('vivimusic', 'Svara'),
    ])

# strings.xml (main) - text only to protect name="..." attributes
changed += fix_xml_text_only(f'{repo}/app/src/main/res/values/strings.xml', [
    ('vivimusic uses the KizzyRPC', 'Svara uses the KizzyRPC'),
    ('vivimusic will only extract your token', 'Svara will only extract your token'),
    ('set Vivi Music to Unrestricted', 'set Svara to Unrestricted'),
    ('Vivi Music', 'Svara'),
    ('vivimusic', 'Svara'),
])
for f in glob.glob(f'{repo}/app/src/main/res/values-*/strings.xml'):
    changed += fix_xml_text_only(f, [
        ('vivimusic', 'Svara'),
        ('Vivi Music', 'Svara'),
        ('ViviMusic', 'Svara'),
    ])

# vivi_strings.xml (main + localized) - text only
vr = [
    ('ViviMusic', 'Svara'),
    ('vivimusic', 'Svara'),
    ('Vivi Music', 'Svara'),
    ('ViviEqualizer', 'SvaraEqualizer'),
    ('Vivi Signature', 'Svara Signature'),
    ('Vivi-Extractor', 'Svara-Extractor'),
    ('Welcome to Vivi', 'Welcome to Svara'),
    ('Vividh for creating vivimusic', 'Yash Agrawal for creating Svara'),
    ('Vividh', 'Yash Agrawal'),
    ('falls back to ViviMusic and Tidal', 'falls back to Svara and Tidal'),
]
changed += fix_xml_text_only(f'{repo}/app/src/main/res/values/vivi_strings.xml', vr)
for f in glob.glob(f'{repo}/app/src/main/res/values-*/vivi_strings.xml'):
    changed += fix_xml_text_only(f, vr)

# metrolist_strings.xml
for f in glob.glob(f'{repo}/app/src/main/res/values*/metrolist_strings.xml', recursive=True):
    changed += fix_xml_text_only(f, [
        ('vivimusic', 'Svara'),
        ('Vivi Music', 'Svara'),
        ('ViviMusic', 'Svara'),
    ])

# AboutScreen.kt
changed += fix(f'{repo}/app/src/main/kotlin/com/music/vivi/ui/screens/settings/AboutScreen.kt', [
    ('vividhpashokan', 'yashagrawal'),
    ('Vividh P Ashokan', 'Yash Agrawal'),
    ('vivizzz007', 'ayash7779-star'),
    ('vivimusicapp', 'svara_app'),
    ('vivimusic.mkmdevilmi.workers.dev', 'github.com/ayash7779-star/vivi-music'),
])

# Copyright headers in all Kotlin files
for f in glob.glob(f'{repo}/app/src/main/kotlin/com/music/vivi/**/*.kt', recursive=True):
    changed += fix(f, [
        ('vivimusic Project (C) 2026', 'Svara Project (C) 2026 by Yash Agrawal'),
        ('vivimusic Project', 'Svara Project (C) 2026 by Yash Agrawal'),
    ])

# shortcuts.xml
changed += fix(f'{repo}/app/src/main/res/xml/shortcuts.xml', [
    ('VIVI MUSIC', 'SVARA'),
    ('Vivi Music', 'Svara'),
])

# CastOptionsProvider.kt
changed += fix(f'{repo}/app/src/main/kotlin/com/music/vivi/cast/CastOptionsProvider.kt', [
    ('VIVI', 'SVARA'),
    ('Vivi Music', 'Svara'),
    ('vivimusic', 'Svara'),
])

# ════════════════════════════════════════════════════════════════
# 2. JIOSAAVN AS PRIMARY STREAM PROVIDER
#    The original code reads EnableSaavnStreamingKey (boolean, default false).
#    We change the default to TRUE so JioSaavn is used for ALL playback.
#    When JioSaavn can't find a match, it falls back to YouTube automatically.
# ════════════════════════════════════════════════════════════════
print("=== JIOSAAVN PRIMARY STREAM ===")

# Fix 1: Change EnableSaavnStreamingKey default from false to true in YTPlayerUtils.kt
yt = f'{repo}/app/src/main/kotlin/com/music/vivi/utils/YTPlayerUtils.kt'
if os.path.exists(yt):
    with open(yt, 'r', encoding='utf-8') as f:
        c = f.read()
    orig = c
    # Change the default value from false to true
    c = c.replace(
        'context.dataStore.get(EnableSaavnStreamingKey, false)',
        'context.dataStore.get(EnableSaavnStreamingKey, true)'
    )
    if c != orig:
        with open(yt, 'w', encoding='utf-8') as f:
            f.write(c)
        print("  OK: EnableSaavnStreamingKey default changed to true in YTPlayerUtils.kt")
        changed += 1
    else:
        print("  SKIP: already changed or pattern not found")

# Fix 2: Also change default in any other files that read EnableSaavnStreamingKey
for f in glob.glob(f'{repo}/app/src/main/kotlin/com/music/vivi/**/*.kt', recursive=True):
    changed += fix(f, [
        ('get(EnableSaavnStreamingKey, false)', 'get(EnableSaavnStreamingKey, true)'),
    ])

# ════════════════════════════════════════════════════════════════
# 3. HIDE VIDEOS by default
# ════════════════════════════════════════════════════════════════
print("=== HIDE VIDEOS ===")

for f in glob.glob(f'{repo}/app/src/main/kotlin/com/music/vivi/**/*.kt', recursive=True):
    changed += fix(f, [
        ('dataStore.get(HideVideoSongsKey, false)', 'dataStore.get(HideVideoSongsKey, true)'),
        ('get(HideVideoSongsKey, false)', 'get(HideVideoSongsKey, true)'),
    ])

# ════════════════════════════════════════════════════════════════
# 4. PUBLIC DOWNLOADS
#    After download completes, copy to Downloads/Svara/ folder.
#    Uses downloadCache (SimpleCache) and CacheDataSource to read
#    the cached content, then writes to public Downloads directory.
# ════════════════════════════════════════════════════════════════
print("=== PUBLIC DOWNLOADS ===")

du = f'{repo}/app/src/main/kotlin/com/music/vivi/playback/DownloadUtil.kt'
if os.path.exists(du):
    with open(du, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'copyToPublicDownloads' not in c:
        # Add imports
        if 'import android.os.Environment' not in c:
            c = c.replace(
                'import java.time.LocalDateTime',
                'import android.os.Environment\nimport java.io.File\nimport java.io.FileOutputStream\nimport java.time.LocalDateTime'
            )
        # Add DataSpec import
        if 'import androidx.media3.datasource.DataSpec' not in c:
            c = c.replace(
                'import androidx.media3.datasource.ResolvingDataSource',
                'import androidx.media3.datasource.DataSpec\nimport androidx.media3.datasource.ResolvingDataSource'
            )
        # Add the copy call inside onDownloadChanged when STATE_COMPLETED
        c = c.replace(
            'Download.STATE_COMPLETED -> {\n                                    database.updateDownloadedInfo(download.request.id, true, LocalDateTime.now())\n                                }',
            'Download.STATE_COMPLETED -> {\n                                    database.updateDownloadedInfo(download.request.id, true, LocalDateTime.now())\n                                    copyToPublicDownloads(download.request.id)\n                                }'
        )
        # Add the copy method before the last closing brace
        copy_method = '''
    private fun copyToPublicDownloads(mediaId: String) {
        try {
            val spans = downloadCache.getCachedSpans(mediaId)
            if (spans.isEmpty()) return
            val downloadsDir = File(
                Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS),
                "Svara"
            )
            if (!downloadsDir.exists()) downloadsDir.mkdirs()
            val destFile = File(downloadsDir, "$mediaId.mp3")
            val cacheDataSource = CacheDataSource.Factory()
                .setCache(downloadCache)
                .setUpstreamDataSourceFactory(
                    androidx.media3.datasource.okhttp.OkHttpDataSource.Factory()
                )
                .createDataSource()
            cacheDataSource.open(DataSpec(mediaId.toUri()))
            FileOutputStream(destFile).use { output ->
                val buffer = ByteArray(8192)
                while (true) {
                    val read = cacheDataSource.read(buffer, 0, buffer.size)
                    if (read < 0) break
                    output.write(buffer, 0, read)
                }
            }
            cacheDataSource.close()
            android.util.Log.i("DownloadUtil", "Copied to public Downloads: ${destFile.absolutePath}")
        } catch (e: Exception) {
            android.util.Log.e("DownloadUtil", "Error copying to public Downloads", e)
        }
    }
'''
        last_brace = c.rstrip().rfind('}')
        if last_brace > 0:
            c = c[:last_brace] + copy_method + '\n' + c[last_brace:]
        with open(du, 'w', encoding='utf-8') as f:
            f.write(c)
        print("  OK: public downloads added to DownloadUtil")
        changed += 1
    else:
        print("  SKIP: copyToPublicDownloads already present")

# Manifest: add WRITE_EXTERNAL_STORAGE for old Android versions
mf = f'{repo}/app/src/main/AndroidManifest.xml'
if os.path.exists(mf):
    with open(mf, 'r', encoding='utf-8') as f:
        mc = f.read()
    if 'WRITE_EXTERNAL_STORAGE' not in mc:
        mc = mc.replace(
            '<uses-permission android:name="android.permission.INTERNET" />',
            '<uses-permission android:name="android.permission.INTERNET" />\n    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28" />'
        )
        with open(mf, 'w', encoding='utf-8') as f:
            f.write(mc)
        print("  OK: added WRITE_EXTERNAL_STORAGE to manifest")
        changed += 1
    else:
        print("  SKIP: WRITE_EXTERNAL_STORAGE already present")

print(f"\n=== DONE: {changed} files changed ===")
