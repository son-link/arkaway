#!/bin/bash

if [ ! -d package ]; then mkdir package; fi

echo "Prepare the package"
cp main.py assets.pyxres maps.json package
cd package
pyxel package . main.py
mv package.pyxapp ../arkaway.pyxapp
cd ..
echo "To HTML"
pyxel app2html arkaway.pyxapp
mv arkaway.html index.html
echo "Clean"
rm -r package
echo "End"