"""
This helper utility safely loads and executes an interface class definition from source text.

Why we need this:
-----------------
When a class decorated with @interface is defined dynamically (for example, inside a test method),
the Python `inspect.getsource()` function cannot retrieve its source code because the class
does not exist in a physical .py file. Our metaclass logic depends on retrieving the real
source text to validate forbidden constructs like explicit getters, setters, or deleters.

This helper writes the provided class definition into a temporary Python file,
imports it as a real module, executes it (triggering any decorators),
and finally removes the file after execution. The decorated interface class is then
returned for further assertions in test cases.
"""

import os
import sys
import uuid
import textwrap
import tempfile
import importlib.util


def load_interface_from_source(source_text: str, class_name: str):
    # Dedent in case the source is written with indentation in the test
    source_text = textwrap.dedent(source_text)

    # Create a temporary Python file to hold the class definition
    temporary_file = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False)
    try:
        # Write the class source code into the file
        temporary_file.write(source_text)
        temporary_file.flush()
        temporary_name = temporary_file.name
    finally:
        # Always close the temporary file handle
        temporary_file.close()

    # Create a unique module name to avoid caching collisions in sys.modules
    module_name = "temp_interface_module_" + uuid.uuid4().hex

    # Build an import specification from the temporary file
    spec = importlib.util.spec_from_file_location(module_name, temporary_name)

    # Create a new module object based on that specification
    module_object = importlib.util.module_from_spec(spec)

    # Register the module temporarily in sys.modules
    sys.modules[module_name] = module_object

    try:
        # Execute the module (this triggers decorator logic, e.g. @interface)
        spec.loader.exec_module(module_object)
    finally:
        # Clean up the temporary file after execution
        try:
            os.unlink(temporary_name)
        except OSError:
            pass

    # Retrieve and return the interface class object from the executed module
    return getattr(module_object, class_name)
