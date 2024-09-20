# Forward to repgen.__main__ for backwards compatibility
# Ensures this can be ran normally via download/direct reference but also as a pypi module/cli tool
import runpy

if __name__ == "__main__":
    runpy.run_module("repgen.__main__", run_name="__main__")