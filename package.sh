mkdir build
zip -r build/repgen.zip __main__.py
zip -r build/repgen.zip repgen
zip -r build/repgen.zip LICENSE.md
echo '#!/usr/bin/env python3' | cat - build/repgen.zip > build/repgen
chmod +x build/repgen