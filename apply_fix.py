#!/usr/bin/env python3
"""Apply the stream provider fix to vivi-music source files.
Run from the repo root: python3 apply_fix.py
"""
import re, sys, os

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

# 1. PreferenceKeys.kt
patch_file(f"{repo}/app/src/main/kotlin/com/music/vivi/constants/PreferenceKeys.kt",
    '// JioSaavn streaming\n',
    '''// Stream provider selection \u2014 replaces the old boolean Saavn toggle.
// JIOSAAVN is the default so music is fetched from JioSaavn first,
// falling back to YouTube Music if a match isn't found.
val StreamProviderKey = stringPreferencesKey("streamProvider")

enum class StreamProvider(val displayName: String) {
    JIOSAAVN("JioSaavn"),
    YOUTUBE_MUSIC("YouTube Music"),
    SPOTIFY("Spotify"),
    APPLE_MUSIC("Apple Music"),
    TIDAL("Tidal");

    companion object {
        fun fromValue(value: String?): StreamProvider =
            entries.find { it.name == value } ?: JIOSAAVN
    }
}

// Kept for backward-compatible migration and JioSettings UI
''')

# 2. MusicService.kt - add imports
patch_file(f"{repo}/app/src/main/kotlin/com/music/vivi/playback/MusicService.kt",
    'import com.music.vivi.constants.AudioQualityKey\n',
    'import com.music.vivi.constants.AudioQualityKey\nimport com.music.vivi.constants.StreamProvider\nimport com.music.vivi.constants.StreamProviderKey\nimport com.music.vivi.constants.SaavnAudioQualityKey\n')

# 2b. MusicService.kt - add watchers after the IP version watcher block
# We insert before the combine(playerVolume...) line
patch_file(f"{repo}/app/src/main/kotlin/com/music/vivi/playback/MusicService.kt",
    '        combine(playerVolume, isMuted) { volume, muted ->',
    '''        // BUG FIX: Watch for stream provider changes - clear cache and reload
        scope.launch {
            dataStore.data
                .map { it[StreamProviderKey]?.let { v -> StreamProvider.fromValue(v) }
                    ?: StreamProvider.JIOSAAVN }
                .distinctUntilChanged()
                .collect { newProvider ->
                    Timber.tag("MusicService").i("STREAM PROVIDER: $newProvider")
                    if (isFirstQualityEmit) return@collect
                    Timber.tag("MusicService").i("STREAM PROVIDER CHANGED -> $newProvider")
                    val mediaId = player.currentMediaItem?.mediaId ?: return@collect
                    val currentPosition = player.currentPosition
                    val currentIndex = player.currentMediaItemIndex
                    val wasPlaying = player.isPlaying
                    songUrlCache.clear()
                    runBlocking(Dispatchers.IO) {
                        try {
                            playerCache.removeResource(mediaId)
                            downloadCache.removeResource(mediaId)
                        } catch (e: Exception) {
                            Timber.tag("MusicService").e(e, "Failed to clear cache on provider change")
                        }
                    }
                    bypassCacheForQualityChange.add(mediaId)
                    player.stop()
                    player.seekTo(currentIndex, currentPosition)
                    player.prepare()
                    if (wasPlaying) player.play()
                }
        }

        // BUG FIX: Watch for Saavn audio quality changes - clear cache and reload
        scope.launch {
            dataStore.data
                .map { it[SaavnAudioQualityKey] ?: com.music.vivi.constants.SaavnAudioQuality.QUALITY_320.name }
                .distinctUntilChanged()
                .collect { newSaavnQuality ->
                    Timber.tag("MusicService").i("SAAVN QUALITY: $newSaavnQuality")
                    if (isFirstQualityEmit) return@collect
                    Timer.tag("MusicService").i("SAAVN QUALITY CHANGED -> $newSaavnQuality")
                    val mediaId = player.currentMediaItem?.mediaId ?: return@collect
                    val currentPosition = player.currentPosition
                    val currentIndex = player.currentMediaItemIndex
                    val wasPlaying = player.isPlaying
                    songUrlCache.clear()
                    runBlocking(Dispatchers.IO) {
                        try {
                            playerCache.removeResource(mediaId)
                            downloadCache.removeResource(mediaId)
                        } catch (e: Exception) {
                            Timber.tag("MusicService").e(e, "Failed to clear cache on Saavn quality change")
                        }
                    }
                    bypassCacheForQualityChange.add(mediaId)
                    player.stop()
                    player.seekTo(currentIndex, currentPosition)
                    player.prepare()
                    if (wasPlaying) player.play()
                }
        }

        combine(playerVolume, isMuted) { volume, muted ->''')

# 3. OldPlayerMenu.kt
patch_file(f"{repo}/app/src/main/kotlin/com/music/vivi/ui/menu/OldPlayerMenu.kt",
    'import com.music.vivi.constants.EnableSaavnStreamingKey\nimport com.music.vivi.utils.rememberPreference\n',
    'import com.music.vivi.constants.StreamProvider\nimport com.music.vivi.constants.StreamProviderKey\nimport com.music.vivi.utils.rememberEnumPreference\n')
patch_file(f"{repo}/app/src/main/kotlin/com/music/vivi/ui/menu/OldPlayerMenu.kt",
    'val (saavnEnabled) = rememberPreference(EnableSaavnStreamingKey, defaultValue = false)',
    'val (streamProvider) = rememberEnumPreference(StreamProviderKey, defaultValue = StreamProvider.JIOSAAVN)\n    val saavnEnabled = streamProvider == StreamProvider.JIOSAAVN')

# 4. PlayerMenu.kt
patch_file(f"{repo}/app/src/main/kotlin/com/music/vivi/ui/menu/PlayerMenu.kt",
    'import com.music.vivi.constants.EnableSaavnStreamingKey\nimport com.music.vivi.utils.rememberPreference\n',
    'import com.music.vivi.constants.StreamProvider\nimport com.music.vivi.constants.StreamProviderKey\nimport com.music.vivi.utils.rememberEnumPreference\n')
patch_file(f"{repo}/app/src/main/kotlin/com/music/vivi/ui/menu/PlayerMenu.kt",
    'val (saavnEnabled) = rememberPreference(EnableSaavnStreamingKey, defaultValue = false)',
    'val (streamProvider) = rememberEnumPreference(StreamProviderKey, defaultValue = StreamProvider.JIOSAAVN)\n    val saavnEnabled = streamProvider == StreamProvider.JIOSAAVN')

# 5. JioSettings.kt
patch_file(f"{repo}/app/src/main/kotlin/com/music/vivi/ui/screens/settings/JioSettings.kt",
    'import com.music.vivi.constants.EnableSaavnStreamingKey\n',
    'import com.music.vivi.constants.StreamProvider\nimport com.music.vivi.constants.StreamProviderKey\n')
patch_file(f"{repo}/app/src/main/kotlin/com/music/vivi/ui/screens/settings/JioSettings.kt",
    '''    val (saavnEnabled, onSaavnEnabledChange) = rememberPreference(
        EnableSaavnStreamingKey,
        defaultValue = false
    )''',
    '''    val (streamProvider, onStreamProviderChange) = rememberEnumPreference(
        StreamProviderKey,
        defaultValue = StreamProvider.JIOSAAVN
    )
    val saavnEnabled = streamProvider == StreamProvider.JIOSAAVN
    val onSaavnEnabledChange: (Boolean) -> Unit = { enable ->
        onStreamProviderChange(if (enable) StreamProvider.JIOSAAVN else StreamProvider.YOUTUBE_MUSIC)
    }''')

# 6. PlayerSettings.kt
patch_file(f"{repo}/app/src/main/kotlin/com/music/vivi/ui/screens/settings/PlayerSettings.kt",
    'import com.music.vivi.constants.EnableSaavnStreamingKey\n',
    'import com.music.vivi.constants.StreamProvider\nimport com.music.vivi.constants.StreamProviderKey\n')
patch_file(f"{repo}/app/src/main/kotlin/com/music/vivi/ui/screens/settings/PlayerSettings.kt",
    '''    val (saavnEnabled, _) = rememberPreference(
        EnableSaavnStreamingKey,
        defaultValue = false
    )
    val (saavnQuality, _) = rememberEnumPreference(''',
    '    val (saavnQuality, _) = rememberEnumPreference(')
patch_file(f"{repo}/app/src/main/kotlin/com/music/vivi/ui/screens/settings/PlayerSettings.kt",
    '''    var showAudioQualityDialog by remember {
        mutableStateOf(false)
    }''',
    '''    val (streamProvider, onStreamProviderChange) = rememberEnumPreference(
        StreamProviderKey,
        defaultValue = StreamProvider.JIOSAAVN
    )

    var showAudioQualityDialog by remember {
        mutableStateOf(false)
    }
    var showStreamProviderDialog by remember {
        mutableStateOf(false)
    }''')
patch_file(f"{repo}/app/src/main/kotlin/com/music/vivi/ui/screens/settings/PlayerSettings.kt",
    '''                // JioSaavn settings navigation
                add(Material3SettingsItem(
                    icon = painterResource(R.drawable.graphic_eq),
                    title = { Text(stringResource(R.string.jiosaavn_settings)) },
                    description = {
                        Text(
                            if (saavnEnabled) {''ÉËˆ	ÉÉÈËÈİ™X[H›İšY\ˆÙ[Xİ[Û‚ˆY
X]\šX[ÔÙ][™ÜÒ][JˆXÛÛˆHZ[\”™\Ûİ\˜ÙJ‹™˜]ØX›K™Ü˜\X×Ù\JKˆ]HHÈ^
İš[™Ô™\Ûİ\˜ÙJ‹œİš[™Ëœİ™X[WÜ›İšY\ŠJHKˆ\ØÜš\[ÛˆHÂˆ^
ˆÚ[ˆ
İ™X[T›İšY\ŠHÂˆİ™X[T›İšY\‹’’SÔĞPU“ˆOˆYˆ
ØX]›”]X[]HOHØX]›]Y[Ô]X[]K”UPSUWÌÌŒ
Bˆ‰Ôİ™X[T›İšY\‹’’SÔĞPU“‹™\Ü^S˜[Y_HLŒŒˆ	ÜØX]›”]X[]KÓX™[

_H‚ˆ[ÙBˆ‰Ôİ™X[T›İšY\‹’’SÔĞPU“‹™\Ü^S˜[Y_HLŒŒˆ	ÜØX]›”]X[]KÓX™[

_H‚ˆ[ÙHOˆİ™X[T›İšY\‹™\Ü^S˜[YBˆBˆ
BˆKˆÛÛXÚÈHÈÚİÔİ™X[T›İšY\‘X[ÙÈHYHKˆ\Ñ^™\ÜÚ]™HHYBˆ
JBˆËÈš[ÔØX]›ˆ]X[]HÙ][™ÜÈ˜]šYØ][Û‚ˆY
X]\šX[ÔÙ][™ÜÒ][JˆXÛÛˆHZ[\”™\Ûİ\˜ÙJ‹™˜]ØX›K™Ü˜\X×Ù\JKˆ]HHÈ^
İš[™Ô™\Ûİ\˜ÙJ‹œİš[™Ëšš[ÜØX]›—ÜÙ][™ÜÊJHKˆ\ØÜš\[ÛˆHÂˆ^
ˆYˆ
İ™X[T›İšY\ˆOHİ™X[T›İšY\‹’’SÔĞPU“ŠHÉÉÉÊB‚ˆÈËˆU^Y\•][Ëšİœ]ÚÙš[JˆÜ™\ßKØ\ÜÜ˜ËÛXZ[‹ÚÛİ[‹ØÛÛKÛ]\ÚXËİš]šKİ][ËÖU^Y\•][Ëšİ‹ˆ	Ú[\ÜÛÛK›]\ÚXËš]šK˜ÛÛœİ[Ë‘[˜X›TØX]›”İ™X[Z[™ÒÙ^W‰Ëˆ	Ú[\ÜÛÛK›]\ÚXËš]šK˜ÛÛœİ[Ë”İ™X[T›İšY\—š[\ÜÛÛK›]\ÚXËš]šK˜ÛÛœİ[Ë”İ™X[T›İšY\’Ù^W‰ÊBœ]ÚÙš[JˆÜ™\ßKØ\ÜÜ˜ËÛXZ[‹ÚÛİ[‹ØÛÛKÛ]\ÚXËİš]šKİ][ËÖU^Y\•][Ëšİ‹ˆ	ÉÉÈ˜[ØX]›‘[˜X›YHÛÛ^™]TİÜ™K™Ù]
[˜X›TØX]›”İ™X[Z[™ÒÙ^K˜[ÙJBˆYˆ
ØX]›‘[˜X›Y
HÉÌ²rÀ¢rrrfÂ&÷f–FW%7G"Ò6öçFW‡BæFF7F÷&RævWB…7G&VÕ&÷f–FW$¶W’Â7G&VÕ&÷f–FW"ä¤”õ4dâææÖR¢fÂ&÷f–FW"Ò7G&VÕ&÷f–FW"æg&öÕfÇVR‡&÷f–FW%7G"¢–b‡&÷f–FW"ÓÒ7G&VÕ&÷f–FW"ä¤”õ4dâ’²rrr ¢2‚â7G&–æw2ç†ÖÀ§F6…öf–ÆR†b'·&W÷Òö÷7&2öÖ–â÷&W2÷fÇVW2÷7G&–æw2ç†ÖÂ"À¢rÇ7G&–æræÖSÒ&Væ&ÆU÷6få÷7G&VÖ–æuöFW62#å7G&VÒVF–òg&öÒ¦–õ6fâ–ç7FVBöb–÷UGV&R×W6–2†fÆÇ2&6²Fò•B–bæ÷Bf–Æ&ÆR“Â÷7G&–æsåÆârÀ¢rÇ7G&–æræÖSÒ&Væ&ÆU÷6få÷7G&VÖ–æuöFW62#å7G&VÒVF–òg&öÒ¦–õ6fâ–ç7FVBöb–÷UGV&R×W6–2†fÆÇ2&6²Fò•B–bæ÷Bf–Æ&ÆR“Â÷7G&–æsåÆâÇ7G&–æræÖSÒ'7G&VÕ÷&÷f–FW"#å7G&VÒ&÷f–FW#Â÷7G&–æsåÆâr §&–çB‚%ÆäFöæRÆÂF6†W2Æ–VBâ" 