[app]
title = JARVIS QR Protocol
package.name = jarvisqr
package.domain = org.starkindustries
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# --- Simplified & Robust Requirements ---
requirements = python3,kivy,qrcode,pillow

# --- Android Targeting (Optimized for Android 12/13) ---
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

orientation = portrait
fullscreen = 0

# --- Permissions ---
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# --- Stable Build Options ---
p4a.branch = master
android.allow_backup = True
android.debug_artifacts = False

[buildozer]
# (str) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1
