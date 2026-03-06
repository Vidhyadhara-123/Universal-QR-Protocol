[app]
title = JARVIS QR Protocol
package.name = jarvisqr
package.domain = org.starkindustries
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# --- Simplified & Robust Requirements ---
requirements = python3,kivy,qrcode,pillow

# --- Android Targeting (Modern & Stable) ---
android.api = 35
android.minapi = 24
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
log_level = 2
warn_on_root = 1
