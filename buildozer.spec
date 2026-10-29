[app]
title = PDF Translator
package.name = pdftranslator
package.domain = org.pdftranslator
source.dir = .
source.include_exts = py,kv,png,jpg,ttf,yaml,json,js,conf,txt,properties

version = 1.0.0

requirements = python3,kivy==2.3.1,kivymd==0.6.14,requests,pyyaml,pdfplumber,fpdf2,pillow

orientation = portrait
fullscreen = False
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1

# Build outputs will land in ./bin
bin_dir = ./bin

[buildozer:android]
# Optimizations
p4a.bootstrap = sdl2
p4a.allow_patches = false
p4a.ignore_libs = org.kivy.sdl2

# Gradle optimizations
android.gradle_dependencies = 
android.manifest_placeholders = 
android.use_javac = false
android.build_type = release
android.numeric_version = 100

# Release signing
android.sign = true
android.keystore = keystore.jks
android.signkey = pdftranslator
android.keystorepw = android
android.signkeypw = android
