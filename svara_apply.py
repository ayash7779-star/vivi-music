#!/usr/bin/env python3
"""
Svara modification script — runs inside GitHub Actions.
Rebrands Vivi Music → Svara, adds AUTO_BEST stream provider,
enables video hiding by default, and copies downloads to public Downloads/Svara/.
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

repo = sys.argv[1] if len(sys.argv) > 1 else '.'
changed = 0

# 1. REBRAND
print("=== REBRAND ===")
changed += fix(f'{repo}/app/src/main/res/values/app_name.xml', [('>VIVI<', '>Svara<')])
changed += fix(f'{repo}/app/src/debug/res/values/app_name.xml', [('>VIVI Debug<', '>Svara Debug<')])
changed += fix(f'{repo}/app/src/main/res/values/updater_strings.xml', [
    ('>VIVI MUSIC version', '>Svara version'),
    ('>VIVI MUSIC<', '>SVARA<'),
    ('>VIVIDH P ASHOKAN<', '>YASH AGRAWAL<'),
    ('vivi-music %1$s', 'Svara %1$s'),
    ('vivi-music', 'Svara'),
])
for f in glob.glob(f'{repo}/app/src/main/res/values-*/updater_strings.xml'):
    changed += fix(f, [('VIVI MUSIC', 'SVARA'), ('VIVIDH P ASHOKAN', 'YASH AGRAWAL'), ('vivi-music', 'Svara'), ('Vivi Music', 'Svara'), ('vivimusic', 'Svara')])
changed += fix(f'{repo}/app/src/main/res/values/strings.xml', [
    ('vivimusic uses the KizzyRPC', 'Svara uses the KizzyRPC'),
    ('vivimusic will only extract your token', 'Svara will only extract your token'),
    ('set Vivi Music to Unrestricted', 'set Svara to Unrestricted'),
    ('Vivi Music', 'Svara'), ('vivimusic', 'Svara'),
])
for f in glob.glob(f'{repo}/app/src/main/res/values-*/strings.xml'):
    changed += fix(f, [('vivimusic', 'Svara'), ('Vivi Music', 'Svara'), ('ViviMusic', 'Svara')])
vr = [('ViviMusic', 'Svara'), ('vivimusic', 'Svara'), ('Vivi Music', 'Svara'), ('ViviEqualizer', 'SvaraEqualizer'), ('Vivi Signature', 'Svara Signature'), ('Vivi-Extractor', 'Svara-Extractor'), ('Welcome to Vivi', 'Welcome to Svara'), ('Vividh for creating vivimusic', 'Yash Agrawal for creating Svara'), ('Vividh', 'Yash Agrawal'), ('falls back to ViviMusic and Tidal', 'falls back to Svara and Tidal')]
changed += fix(f'{repo}/app/src/main/res/values/vivi_strings.xml', vr)
for f in glob.glob(f'{repo}/app/src/main/res/values-*/vivi_strings.xml'):
    changed += fix(f, vr)
changed += fix(f'{repo}/app/src/main/kotlin/com/music/vivi/ui/screens/settings/AboutScreen.kt', [
    ('vividhpashokan', 'yashagrawal'), ('Vividh P Ashokan', 'Yash Agrawal'),
    ('vivizzz007', 'ayash7779-star'), ('vivimusicapp', 'svara_app'),
    ('vivimusic.mkmdevilmi.workers.dev', 'github.com/ayash7779-star/vivi-music'),
])
for f in glob.glob(f'{repo}/app/src/main/kotlin/com/music/vivi/**/*.kt', recursive=True):
    changed += fix(f, [('vivimusic Project (C) 2026', 'Svara Project (C) 2026 by Yash Agrawal'), ('vivimusic Project', 'Svara Project (C) 2026 by Yash Agrawal')])
changed += fix(f'{repo}/app/src/main/res/xml/shortcuts.xml', [('VIVI MUSIC', 'SVARA'), ('Vivi Music', 'Svara')])
changed += fix(f'{repo}/app/src/main/kotlin/com/music/vivi/cast/CastOptionsProvider.kt', [('VIVI', 'SVARA'), ('Vivi Music', 'Svara'), ('vivimusic', 'Svara')])
sp = f'{repo}/app/src/main/res/values/strings.xml'
if os.path.exists(sp):
    with open(sp, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'stream_provider' not in c:
        c = c.replace('</resources>', '    <string name="stream_provider">Stream Provider</string>\n</resources>')
        with open(sp, 'w', encoding='utf-8') as f:
            f.write(c)
        print("  OK: added stream_provider string"); changed += 1

# 2. AUTO_BEST
print("=== AUTO_BEST ===")
pk = f'{repo}/app/src/main/kotlin/com/music/vivi/constants/PreferenceKeys.kt'
if os.path.exists(pk):
    with open(pk, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'AUTO_BEST' not in c:
        c = c.replace('enum class StreamProvider(val displayName: String) {\n    JIOSAAVN("JioSaavn"),', 'enum class StreamProvider(val displayName: String) {\n    AUTO_BEST("Auto (Best Quality)"),\n    JIOSAAVN("JioSaavn"),')
        with open(pk, 'w', encoding='utf-8') as f:
            f.write(c)
        print("  OK: added AUTO_BEST to enum"); changed += 1
    else:
        print("  SKIP: already present")

# 3. YTPlayerUtils AUTO_BEST logic
print("=== YTPlayerUtils ===")
yt = f'{repo}/app/src/main/kotlin/com/music/vivi/utils/YTPlayerUtils.kt'
if os.path.exists(yt):
    with open(yt, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'AUTO_BEST' not in c:
        c = c.replace('if (provider == StreamProvider.JIOSAAVN) {', 'if (provider == StreamProvider.JIOSAAVN || provider == StreamProvider.AUTO_BEST) {')
        c = c.replace('if (provider == StreamProvider.JIOSAAVN || provider == StreamProvider.AUTO_BEST) {\n                Timber.tag(TAG).d("JioSaavn streaming enabled', 'if (provider == StreamProvider.JIOSAAVN || provider == StreamProvider.AUTO_BEST) {\n                val saavnQualityOverride = if (provider == StreamProvider.AUTO_BEST) SaavnAudioQuality.QUALITY_320 else null\n                Timber.tag(TAG).d("JioSaavn streaming enabled')
        c = c.replace('val qualityKey = context.dataStore.get(SaavnAudioQualityKey, SaavnAudioQuality.QUALITY_320.name)\n                    val quality = runCatching { SaavnAudioQuality.valueOf(qualityKey) }\n                        .getOrDefault(SaavnAudioQuality.QUALITY_320)', 'val quality = saavnQualityOverride ?: run {\n                        val qualityKey = context.dataStore.get(SaavnAudioQualityKey, SaavnAudioQuality.QUALITY_320.name)\n                        runCatching { SaavnAudioQuality.valueOf(qualityKey) }.getOrDefault(SaavnAudioQuality.QUALITY_320)\n                    }')
        c = c.replace('if (saavnResult != null) {\n                    return Result.success(saavnResult)\n                }', 'if (saavnResult != null && provider == StreamProvider.JIOSAAVN) {\n                    return Result.success(saavnResult)\n                }\n                if (saavnResult != null && provider == StreamProvider.AUTO_BEST) {\n                    val saavnBitrate = saavnResult.format.bitrate ?: 0\n                    if (saavnBitrate >= 320_000) return Result.success(saavnResult)\n                    val ytResult = resolvePlaybackData(videoId, playlistId, AudioQuality.HIGH, connectivityManager)\n                    if (ytResult.isSuccess) {\n                        val ytBitrate = ytResult.getOrNull()?.format?.bitrate ?: 0\n                        if (ytBitrate > saavnBitrate) {\n                            Timber.tag(TAG).i("AUTO_BEST: YT bitrate=$ytBitrate > Saavn=$saavnBitrate")\n                            return ytResult\n                        }\n                    }\n                    return Result.success(saavnResult)\n                }')
        with open(yt, 'w', encoding='utf-8') as f:
            f.write(c)
        print("  OK: AUTO_BEST logic added"); changed += 1
    else:
        print("  SKIP: already present")

# 4. HIDE VIDEOS by default
print("=== HIDE VIDEOS ===")
for f in glob.glob(f'{repo}/app/src/main/kotlin/com/music/vivi/**/*.kt', recursive=True):
    changed += fix(f, [('dataStore.get(HideVideoSongsKey, false)', 'dataStore.get(HideVideoSongsKey, true)'), ('get(HideVideoSongsKey, false)', 'get(HideVideoSongsKey, true)')])

# 5. PUBLIC DOWNLOADS
print("=== PUBLIC DOWNLOADS ===")
du = f'{repo}/app/src/main/kotlin/com/music/vivi/playback/DownloadUtil.kt'
if os.path.exists(du):
    with open(du, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'copyToPublicDownloads' not in c:
        if 'import android.os.Environment' not in c:
            c = c.replace('import java.time.LocalDateTime', 'import android.os.Environment\nimport java.io.File\nimport java.io.FileOutputStream\nimport java.time.LocalDateTime')
        c = c.replace('if (download.state == Download.STATE_FAILED) {\n                    Timber.tag("DownloadUtil").e("Download failed: ${download.request.id}")\n                }', 'if (download.state == Download.STATE_FAILED) {\n                    Timber.tag("DownloadUtil").e("Download failed: ${download.request.id}")\n                }\n                if (download.state == Download.STATE_COMPLETED) {\n                    scope.launch {\n                        try {\n                            val mediaId = download.request.id\n                            val song = database.song(mediaId)\n                            val title = song?.title ?: mediaId\n                            val artist = song?.artists?.joinToString(", ") { it.name } ?: ""\n                            copyToPublicDownloads(mediaId, title, artist)\n                        } catch (e: Exception) {\n                            Timber.tag("DownloadUtil").e(e, "Failed to copy to public Downloads")\n                        }\n                    }\n                }')
        copy_method = '''
    private fun copyToPublicDownloads(mediaId: String, title: String, artist: String) {
        try {
            val cachedFile = downloadCache.getCacheFile(mediaId, 0, -1, 0) ?: return
            if (!cachedFile.exists()) return
            val downloadsDir = File(
                Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS),
                "Svara"
            )
            if (!downloadsDir.exists()) downloadsDir.mkdirs()
            val safeTitle = title.replace(Regex("[^a-zA-Z0-9 ._()-]"), "_").trim()
            val safeArtist = artist.replace(Regex("[^a-zA-Z0-9 ._()-]"), "_").trim()
            val fileName = if (safeArtist.isNotBlank()) "${'$'}safeArtist - ${'$'}safeTitle.mp3" else "${'$'}safeTitle.mp3"
            val destFile = File(downloadsDir, fileName)
            cachedFile.inputStream().use { input ->
                FileOutputStream(destFile).use { output -> input.copyTo(output) }
            }
            Timber.tag("DownloadUtil").i("Copied to public Downloads: ${'$'}{destFile.absolutePath}")
        } catch (e: Exception) {
            Timber.tag("DownloadUtil").e(e, "Error copying to public Downloads")
        }
    }
'''
        last_brace = c.rstrip().rfind('}')
        if last_brace > 0:
            c = c[:last_brace] + copy_method + '\n' + c[last_brace:]
        with open(du, 'w', encoding='utf-8') as f:
            f.write(c)
        print("  OK: public downloads added"); changed += 1
    else:
        print("  SKIP: already present")
mf = f'{repo}/app/src/main/AndroidManifest.xml'
if os.path.exists(mf):
    with open(mf, 'r', encoding='utf-8') as f:
        mc = f.read()
    if 'WRITE_EXTERNAL_STORAGE' not in mc:
        mc = mc.replace('<uses-permission android:name="android.permission.INTERNET" />', '<uses-permission android:name="android.permission.INTERNET" />\n    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28" />')
        with open(mf, 'w', encoding='utf-8') as f:
            f.write(mc)
        print("  OK: added WRITE_EXTERNAL_STORAGE"); changed += 1
    else:
        print("  SKIP: already present")

print(f"\n=== DONE: {changed} files changed ===")