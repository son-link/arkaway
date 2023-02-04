#!/bin/bash
echo "Build Linux executable"
pyxel app2exe arkaway.pyxapp
cp arkaway AppDir/usr/bin
echo "Build AppImage"
appimage-builder-1.1.0-x86_64.AppImage
