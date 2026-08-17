#!/usr/bin/env python3
"""
Apply Svara rebrand, AUTO_BEST stream provider, and public downloads.
Designed to run on the fork (which has StreamProvider enum).
"""
import os, sys, re, glob

def fix_file(path, replacements, must_exist=True):
    if not os.path.exists(path):
        if must_exist:
            print(f"WARN: {path} not found, skipping")
        return False
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content
    count = 0
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            count += 1
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"OK8 {path} - {count} replacements")
        return True
    else:
        print(f"SKIP: {path} - no changes needed")
        return False

repo = sys.argv[1] if len(sys.argv) > 1 else '.'

#==================================================
# 1. REBRAND: Vivi Music -> Svara, by Yash Agrawal
#===================================================
print("\n=== 1. REBRANDING ===")

fix_file(os.path.join(repo, 'app/src/main/res/values/app_name.xml'), [
    ('<string name="app_name">VIVI</string>', '<string name="app_name">Svara</string>'),
])

fix_file(os.path.join(repo, 'app/src/debug/res/values/app_name.xml'), [
    ('<string name="app_name">VIVI Debug</string>', '<string name="app_name">Svara Debug</string>'),
])

# epdater_strings.xml
fix_file(os.path.join(repo, 'app/src/main/res/values/updater_strings.xml'), [
    ('>VIVI MUSIC version', '>Svara version'),
    ('>VIVI MUSIC<<', '>SVARA<<'),
    '>VIVID P ASHOKAN<', '>YASH AGRAWAL<<'),
    ('vivi-music %1$s', 'Svara %1$s'),
    ('Vivi Music %1$s', 'Svara %1$s'),
])
for f in glob.glob(os.path.join(repo, 'app/src/main/res/values-*/updater_strings.xml')):
    fix_file(f, [
        ('VIVI MUSIC', 'SVARA'),
        ('VIVID P ASHOKAN', 'YASH AGRAWAL'),
        ('vivi-music', 'Svara'),
        ('Vivi Music', 'Svara'),
        ('vivimusic', 'Svara'),
    ])

# strings.xml
fix_file(os.path.join(repo, 'app/src/main/res/values/strings.xml'), [
    ('vivimusic uses the KizzyRPC', 'Svara uses the KizzyRPC'),
    ('vivi music will only extract your token', 'Svara will only extract your token'),
    ('set Vivi Music to Unrestricted', 'set Svara to Unrestricted'),
])
for f in glob.glob(os.path.join(repo, 'app/src/main/res/values-*/strings.xml')):
    fix_file(f, [
        ('vivifmusic', 'Svara'),
        ('Vivi Music', 'Svara'),
        ('ViviMusic', 'Svara'),
    ])

# vivi strings.xml
vivi_replacements = [
    ('falls back to ViviMusic and Tidal', 'falls back to Svara and Tidal'),
    ('ViviMusic', 'Svara'),
    ('vivimusic', 'Svara'),
    ('Vivi Music', 'Svara'),
    ('ViviEqualizer', 'Svara Equalizer'),
    ('Vivi Signature', 'Svara Signature'),
    ('Vivi-Extractor', 'Svara-Extractor'),
    ('Welcome to Vivi', 'Welcome to Svara'),
    ('Vividh for creating vivi music', 'Yash Agrawal for creating Svara'),
    ('Vividh', 'Yash Agrawal'),
]
fix_file(os.path.join(repo, 'app/src/main/res/values/vivi_strings.xml'), vivi replacements)
for f in glob.glob(os.path.join(repo, 'app/src/main/res/values-*/vivi strings.xml')):
    fix_file(f, vivi_replacements)

# AboutScreen.kt
fix_file(os.path.join(repo, 'app/src/main/kotlin/com/music/vivi/ui/screens/settings/AboutScreen.kt'), [
    ('vividhpashokan', 'yashagrawal'),
    ('Vividh P Ashokan', 'Yash Agrawal'),
    ('vivizzz007', 'ayash7779-star'),
    ('vivi musicapp', 'svara_app'),
    ('vivi music.mkmdevilmi.workers.dev', 'github.com/ayash7779-star/vivi music'),
])

# Copyright headers
for f in glob.glob(os.path.join(repo, 'app/src/main/kotlin/com/music/vivi/**/*.kt'), recursive=True):
    fix_file(f, [
        ('vivi music Project (C) 2026', 'Svara Project (C) 2026 by Yash Agrawal'),
    ], must_exist=False)

# Add stream_provider string
strings_path = os.path.join(repo, 'app/src/main/res/values/strings.xml')
if os.path.exists(strings_path):
    with open(strings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'name="stream_provider"' not in content:
        content = content.replace('</resources>', '    <string name="stream_provider">Stream Provider</string>\n</resources>')
        with open(strings_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("OK: Added stream_provider string")

#=================================================
# 2. ADD AUTO_BEST TO StreamProvider ENUM
#===================================================
print("\n=== 2. ADD AUTO_BEST ===")

pk_path = os.path.join(repo, 'app/src/main/kotlin/com/music/vivi/constants/PreferenceKeys.kt')
if os.path.exists(pk_path):
    with open(pk_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'AUTO_BEST' not in content:
        content = content.replace(
            'enum class StreamProvider(val displayName: String) {\n    JIOSAAVN("JioSaavn"),',
           'enum class StreamProvider(val displayName: String) {
    AUTO_BEST("Auto (Best Quality)"),\n    JIOSAAVN("JioSaavn"),'
        )
        with open(pk_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("OK: Added AUTO_BEST to StreamProvider enum")
    else:
        print("SKIP: AUTO_BEST already exists")

#=================================================
# 3. MODIFY YTPlayerUtils FOR AUTO_BEST
#==================================================
print("\n=== 3. YTPlayerUtils AUTO_BEST ===")

yt_path = os.path.join(repo, 'app/src/main/kotlin/com/music/vivi/utils/YTPlayerUtils.kt')
if os.path.exists(yt_path):
    with open(yt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 3a. Change provider check to also handle AUTO_BEST
    old_check = 'if (provider == StreamProvider.JIOSAAVN) {'
    new_check = 'if (provider == StreamProvider.JIOSAAVN || provider == StreamProvider.AUTO_BEST) {\n            val saavnQualityOverride = if (provider == StreamProvider.AUTO_BEST) SaavnAudioQuality.QUALITY_320 else null'
    if old_check in content:
        content = content.replace(old_check, new_check, 1)
        print("OK: Added AUTO_BEST check")
    
    # 3b. Override quality selection for AUTO_BEST
    old_q = '''                    val qualityKey = context.dataStore.get(SaavnAudioQualityKey, SaavnAudioQuality.QUALITY_320.name)\n                val quality = runCatching { SaavnAudioQuality.valueOf(qualityKey) }\n                    .getOrDefault(SaavnAudioQuality.QUALITY_320)'''
    new_q = '''                      val quality = saavnQualityOverride ?: run {
                    val qualityKey = context.dataStore.get(SaavnAudioQualityKey, SaavnAudioQuality.QUALITY_320.name)\n                    runCatching { SaavnAudioQuality.valueOf(qualityKey) }\n                        .getOrDefault(SaavnAudioQuality.QUALITY_320)
                }'''
    if old_q in content:
        content = content.replace(old_q, new_q)
        print("OK: Added quality override")
    
    # 3c. For AUTO_BEST, compare with YouTube and pick higher bitrate
    old_fb = '''            if (saavnResult != null) {
                return Result.success(saavnResult)
            }'''
    new_fb = '''            if (saavnResult != null && provider == StreamProvider.JIOSAAVN) {
                return Result.success(saavnResult)
            }
              if (saavnResult != null && provider == StreamProvider.AUTO_BEST) {
                    val saavnBitrate = saavnResult.format.bitrate ?: 0
                    if (saavnBitrate >= 320_000) {
                        return Result.success(saavnResult)
                    }
                    val ytResult = resolvePlaybackData(videoId, playlistId, AudioQuality.HIGH, connectivityManager)
                    if (ytResult.isSuccess) {
                        val ytBitrate = ytResult.getOrNull()?.format?.bitrate ?: 0
                        if (ytBitrate > saavnBitrate) {
                            Timber.tag(TAG).i("AUTO_BEST. YT bitrate=$ytBitrate > Saavn=$saavnBitrate")
                            return ytResult
                        }
                    }
                    return Result.success(saavnResult)
                }'''
    if old_fb in content:
        content = content.replace(old_fb, new_fb)
        print("OK: Added AUTO_BEST comparison")
    
    # 3d. Force YouTube HIGH quality for AUTO_BEST
    old_res = 'val firstAttempt = resolvePlaybackData(videoId, playlistId, audioQuality, connectivityManager)'
    new_res = '''val effectiveQuality = if (context != null) {
            val p = StreamProvider.fromValue(context.dataStore.get(StreamProviderKey, StreamProvider.JIOSAAVN.name))
            if (p == StreamProvider.AUTO_BEST) AudioQuality.HIGH else audioQuality
        } else audioQuality
        val firstAttempt = resolvePlaybackData(videoId, playlistId, effectiveQuality, connectivityManager)'''
    if old_res in content:
        content = content.replace(old_res, new_res)
        print("OK: Added YouTube quality override for AUTO_BEST")
    
    with open(yt_path, 'w', encoding='utf-8') as f:
        f.write(content)

#=================================================
# 4. PUBLIC DOWNLOADS: Copy to Downloads folder
#=================================================
print("\n=== 4. PUBLIC DOWNLOADS ===")

du_path = os.path.join(repo, 'app/src/main/kotlin/com/music/vivi/playback/DownloadUtil.kt')
if os.path.exists(du_path):
    with open(du_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add imports
    if 'import android.os.Environment' not in content:
        content = content.replace(
            'import java.time.LocalDateTime',
            'import android.os.Environment\nimport java.io.File\nimport java.io.FileOutputStream\nimport java.time.LocalDateTime'
        )
        print("OK: Added imports")
    
    # Add copyToPublicDownloads method before the last closing brace
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
            val fileName = if (safeArtist.isNotBlank()) "$safeArtist - $safeTitle.mp3" else "$safeTitle.mp3"
            val destFile = File(downloadsDir, fileName)
            cachedFile.inputStream().use { input =>
                FileOutputStream(destFile).use { output -> input.copyTo(output) }
            }
            val intent = android.content.Intent(android.content.Intent.ACTION_MEDIA_SCANNER_SCAN_FILE)
            intent.data = android.net.Uri.fromFile(destFile)
            appContext.sendBroadcast(intent)
            Timber.tag("DownloadUtil").i("Copied to public Downloads: ${destFile.absolutePath}")
        } catch (e: Exception) {
            Timber.tag("DownloadUtil").e(e, "Error copying to public Downloads")
        }
    }
'''
    
    # Find onDownloadChanged and add the copy call
    old_odc = '''override fun onDownloadChanged(
                downloadManager: DownloadManager,
                download: Download,
                finalException: Exception?,
            ) {
                downloads.update { downloads ->
                    downloads + (download.request.id to download)
                }
                if (download.state == Download.STATE_FAILED) {
                    Timber.tag("DownloadUtil").e("Download failed: ${download.request.id}")
                }
            }'''
    
    new_odc = '''override fun onDownloadChanged(
                downloadManager: DownloadManager,
                download: Download,
                finalException: Exception?,
            ) {
                downloads.update { downloads ->
                    downloads + (download.request.id to download)
                }
                if (download.state == Download.STATE_FAILED) {
                    Timber.tag("DownloadUtil").e("Download failed: ${download.request.id}")
                }
                if (download.state == Download.STATE_COMPLETED) {
                    scope.launch {
                        try {
                            val mediaId = download.request.id
                            val song = database.song(mediaId)
                            val title = song?.title ?: mediaId
                            val artist = song?.artistsString ?: ""
                            copyToPublicDownloads(mediaId, title, artist)
                        } catch (e: Exception) {
                            Timber.tag("DownloadUtil").e(e, "Failed to copy to public Downloads")
                        }
                    }
                }
            }'''
    
    if old_odc in content:
        content = content.replace(old_odc, new_odc)
        print("OK: Updated onDownloadChanged listener")
    else:
        print("WARN: Could not find onDownloadChanged pattern")
    
    # Add the copy method before the last }
    last_brace = content.rstrip().rfind('}')
    if last_brace > 0:
        content = content[:last_brace] + copy_method + '\n' + content[last_brace:]
        print("OK: Added copyToPublicDownloads method")
    
    with open(du_path, 'w', encoding='utf-8') as f:
        f.write(content)

# Add WRITE_EXTERNAL_MORAGE to manifest if missing
manifest_path = os.path.join(repo, 'app/src/main/AndroidManifest.xml')
if os.path.exists(manifest_path):
    with open(manifest_path, 'r', encoding='utf-8') as f:
        mcontent = f.read()
    if 'WRITE_EXTERNAL_STORAGE' not in mcontent:
        mcontent = mcontent.replace(
            '<uses-permission android:name="android.permission.INTERNET" />',
            '<uses-permission android:name="android.permission.INTERNET" />\n    <uses-permission android:name="android.permission.WRITE_EXTERNAL_ORAGE" android:maxSdkVersion="28" />'
        )
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(mcontent)
        print("OK: Added WRITE_EXTERNAL_STORAGE to manifest")

print("\n=== ALL CHANGES APPLIED ===")
