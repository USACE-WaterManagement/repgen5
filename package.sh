#!/bin/sh
dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd $dir
mkdir build 2>/dev/null
python -c "import compileall; compileall.compile_dir('.', quiet=1)"
zip -r build/repgen.zip __main__.py
zip -r build/repgen.zip __pycache__
zip -r build/repgen.zip repgen
zip -r build/repgen.zip LICENSE.md
echo '#!/usr/bin/env python3' | cat - build/repgen.zip > build/repgen
chmod +x build/repgen
