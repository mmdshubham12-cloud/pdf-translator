[app]
title = PDF Translator
package.name = pdftranslator
package.domain = org.pdftranslator
source.dir = .
source.include_exts = py,kv,png,jpg,ttf,yaml,json,js,conf,txt,properties

version = 1.0.0

requirements = python3,kivy==2.3.1,kivymd==1.2.0,requests,pyyaml,pdfplumber,fpdf2,pillow,arabic-reshaper,python-bidi

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
