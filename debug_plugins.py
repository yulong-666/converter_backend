
import sys
import importlib
import pkgutil
import inspect
import app.plugins
from app.plugins.base import BaseConverter

print("Checking plugins...")
package_path = app.plugins.__path__[0] # Use __path__ generic way
package_name = app.plugins.__name__
print(f"Plugins path: {package_path}")

for _, name, _ in pkgutil.iter_modules([package_path]):
    print(f"Found module: {name}")
    if name == "base":
        continue
    
    try:
        module = importlib.import_module(f"{package_name}.{name}")
        print(f"  Successfully imported {name}")
        
        for _, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BaseConverter) and 
                obj is not BaseConverter):
                print(f"    Found converter class: {obj.__name__}")
                try:
                     formats = obj.supported_source_formats()
                     print(f"    Supported formats: {formats}")
                except Exception as e:
                     print(f"    Error calling supported_source_formats: {e}")

    except Exception as e:
        print(f"  FAILED to import {name}: {e}")
