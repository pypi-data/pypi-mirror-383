import os
import sys
import unittest
import importlib.util
from pathlib import Path


if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).parent.parent
    TEST_DIR = PROJECT_ROOT / "test"

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for root, dirs, files in os.walk(TEST_DIR):
        # حذف پوشه benchmark از پیمایش
        if "benchmark" in dirs:
            dirs.remove("benchmark")

        for file in files:
            if file.endswith(".py") and file != "setup.py":
                file_path = os.path.join(root, file)

                module_name = ".".join(Path(file_path).relative_to(PROJECT_ROOT).with_suffix("").parts)

                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)

                    tests = loader.loadTestsFromModule(module)
                    suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=1)
    runner.run(suite)
