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
    '''// Stream provider selection -- replaces the old boolean Saavn toggle.
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
            datastore.data
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
            datastore.data
                .map { it[SaavnAudioQualityKey] ?: com.music.vivi.constants.SaavnAudioQuality.QUALITY_320.name }
                .distinctUntilChanged()
                .collect { newSaavnQuality ->
                    Timber.tag("MusicService").i("SAAVN QUALITY: $newSaavnQuality")
                    if (isFirstQualityEmit) return@collect
                    Timber.tag("MusicService").i("SAAVN QUALITY CHANGED -> $newSaavnQuality")
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
                            if (saavnEnabled) {''',
    '''                // Stream provider selection
                add(Material3SettingsItem(
                    icon = painterResource(R.drawable.graphic_eq),
                    title = { Text(stringResource(R.string.stream_provider)) },
                    description = {
                        Text(
                            when (streamProvider) {
                                StreamProvider.JIOSAAVN -> if (saavnQuality == SaavnAudioQuality.QUALITY_320)
                                    "${StreamProvider.JIOSAAVN.displayName} * ${saavnQuality.toLabel()}"
                                 else
                                    "${StreamProvider.JIOSAAVN.displayName} * ${saavnQuality.toLabel()}"
                                 else -> streamProvider.displayName
                             }
                        )
                    },
                    onClick = { showStreamProviderDialog = true },
                    isExpressive = true
                ))
                // JioSaavn quality settings navigation
                add(Material3SettingsItem(
                    icon = painterResource(R.drawable.graphic_eq),
                    title = { Text(stringResource(R.string.jiosaavn_settings)) },
                    description = {
                        Text(
                            if (streamProvider == StreamProvider.JIOSAAVN) {''')

# 7. YTPlayerUtils.kt
patch_file(f"{repo}/app/src/main/kotlin/com/music/vivi/utils/YTPlayerUtils.kt",
    'import com.music.vivi.constants.EnableSaavnStreamingKey\n',
    'import com.music.vivi.constants.StreamProvider\nimport com.music.vivi.constants.StreamProviderKey\n')
patch_file(f"{repo}/app/src/main/kotlin/com/music/vivi/utils/YTPlayerUtils.kt",
    '''            val saavnEnabled = context.dataStore.get(EnableSaavnStreamingKey, false)
            if (saavnEnabled) {''',
    '''            val providerStr = context.dataStore.get(StreamProviderKey, StreamProvider.JIOSAAVN.name)
            val provider = StreamProvider.fromValue(providerStr)
            if (provider == StreamProvider.JIOSAAVN) {''')

# 8. strings.xml
patch_file(f"{repo}/app/src/main/res/values/strings.xml",
    '    <string name="enable_saavn_streaming_desc">Stream audio from JioSaavn instead of YouTube Music (falls back to YT if not available)</string>\n',
    '    <string name="enable_saavn_streaming_desc">Stream audio from JioSaavn instead of YouTube Music (falls back to YT if not available)</string>\n    <string name="stream_provider">Stream Provider</string>\n')

print("\nDone! All patches applied.")
