[app]
title = JARVIS QR Protocol
package.name = jarvisqr
package.domain = org.starkindustries
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# --- Advanced Requirements ---
requirements = python3,kivy==2.3.0,qrcode,pillow,hostpython3,sdl2,sdl2_image,sdl2_ttf,sdl2_mixer,pythonforandroid

# --- Android Targeting (Android 12/13+) ---
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

orientation = portrait
fullscreen = 0

# --- Android Permissions ---
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# --- Build Options ---
p4a.branch = master
android.allow_backup = True
# Use a custom NDK API level if needed
android.ndk_api = 21
