mkdir build
zip -r build/repgen.zip __main__.py
zip -r build/repgen.zip repgen
echo '#!/bin/env python3' | cat - build/repgen.zip > build/repgen
chmod +x build/repgen