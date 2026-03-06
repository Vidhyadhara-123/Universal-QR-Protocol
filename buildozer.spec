[app]
title = JARVIS QR
package.name = jarvisqr
package.domain = org.starkindustries
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# --- High Stability Requirements ---
requirements = python3,kivy==2.3.0,qrcode,pillow

# --- Rock-Solid Android Targeting ---
android.api = 34
android.minapi = 21
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

orientation = portrait
fullscreen = 0

# --- Permissions ---
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# --- Optimization ---
p4a.branch = master
android.allow_backup = True
android.debug_artifacts = False

[buildozer]
log_level = 2
warn_on_root = 1
