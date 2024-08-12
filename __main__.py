# Forward to repgen.__main__ for backwards compatibility
import runpy

if __name__ == "__main__":
    runpy.run_module("repgen.__main__", run_name="__main__")