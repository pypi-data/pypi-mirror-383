# ObjWatch

[![Python Test Status](https://github.com/aeeeeeep/objwatch/actions/workflows/python-test.yml/badge.svg)](https://github.com/aeeeeeep/objwatch/actions/workflows/python-test.yml)
[![Documentation](https://img.shields.io/badge/docs-latest-green.svg?style=flat)](https://objwatch.readthedocs.io)
[![License](https://img.shields.io/github/license/aeeeeeep/objwatch)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/objwatch)](https://pypi.org/project/objwatch)
[![Downloads](https://static.pepy.tech/badge/objwatch)](https://pepy.tech/projects/objwatch)
[![Python Versions](https://img.shields.io/pypi/pyversions/objwatch)](https://github.com/aeeeeeep/objwatch)
[![GitHub pull request](https://img.shields.io/badge/PRs-welcome-blue)](https://github.com/aeeeeeep/objwatch/pulls)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16986436.svg)](https://doi.org/10.5281/zenodo.16986436)

\[ English | [中文](README_zh.md) \]

## 🔭 Overview

ObjWatch is a robust Python library designed to streamline the debugging and monitoring of complex projects. By offering real-time tracing of object attributes and method calls, ObjWatch empowers developers to gain deeper insights into their codebases, facilitating issue identification, performance optimization, and overall code quality enhancement.

**⚠️ Performance Notice**

ObjWatch may impact your application's performance. It is recommended to use it solely in debugging environments.

## ✨ Features

- **🎯 Flexible Target Monitoring**: Supports multiple target selection modes such as file paths, modules, classes, class members, class methods, functions, and global variables.
- **🌳 Nested Structure Tracing**: Visualize and monitor nested function calls and object interactions with clear, hierarchical logging.
- **📝 Enhanced Logging Support**: Utilize Python's built-in `logging` module for structured, customizable log outputs, including support for simple and detailed formats.
- **📋 Logging Message Types**: ObjWatch categorizes log messages into various types to provide detailed insights into code execution. The primary types include:
  
  - **`run`**: Function/method execution start
  - **`end`**: Function/method execution end
  - **`upd`**: Variable creation
  - **`apd`**: Element addition to data structures
  - **`pop`**: Element removal from data structures
  
  These classifications help developers efficiently trace and debug their code by understanding the flow and state changes within their applications.
- **🔥 Multi-Process Support**: Seamlessly trace distributed applications running across multiple processes/GPUs, ensuring comprehensive monitoring in high-performance environments.
- **🔌 Custom Wrapper Extensions**: Extend ObjWatch's functionality with custom wrappers, allowing tailored tracing and logging to fit specific project needs.
- **🎛️ Context Manager & API Integration**: Integrate ObjWatch effortlessly into your projects using context managers or API functions without relying on command-line interfaces.

## 📦 Installation

ObjWatch is available on [PyPI](https://pypi.org/project/objwatch). Install it using `pip`:

```bash
pip install objwatch
```

Alternatively, you can clone the latest repository and install from source:

```bash
git clone https://github.com/aeeeeeep/objwatch.git
cd objwatch
pip install -e .
```

## 🚀 Getting Started

### Basic Usage

ObjWatch can be utilized as a context manager or through its API within your Python scripts.

#### Using as a Context Manager

```python
import objwatch

def main():
    # Your code
    pass

if __name__ == '__main__':
    with objwatch.ObjWatch(['your_module.py']):
        main()
```

#### Using the API

```python
import objwatch

def main():
    # Your code
    pass

if __name__ == '__main__':
    obj_watch = objwatch.watch(['your_module.py'])
    main()
    obj_watch.stop()
```

### Example Usage

Below is a comprehensive example demonstrating how to integrate ObjWatch into a Python script:

```python
import time
import objwatch
from objwatch.wrappers import BaseWrapper


class SampleClass:
    def __init__(self, value):
        self.value = value

    def increment(self):
        self.value += 1
        time.sleep(0.1)

    def decrement(self):
        self.value -= 1
        time.sleep(0.1)


def main():
    obj = SampleClass(10)
    for _ in range(5):
        obj.increment()
    for _ in range(3):
        obj.decrement()


if __name__ == '__main__':
    # Using ObjWatch as a context manager
    with objwatch.ObjWatch(['examples/example_usage.py'], output='./objwatch.log', wrapper=BaseWrapper):
        main()

    # Using the watch function
    obj_watch = objwatch.watch(['examples/example_usage.py'], output='./objwatch.log', wrapper=BaseWrapper)
    main()
    obj_watch.stop()

```

When running the above script, ObjWatch will generate logs similar to the following:

<details>

<summary>Expected Log Output</summary>

```
Processed targets:
>>>>>>>>>>

<<<<<<<<<<
Filename targets:
>>>>>>>>>>
examples/example_usage.py
<<<<<<<<<<
[2025-05-21 07:49:25] [WARNING] objwatch: wrapper 'BaseWrapper' loaded
[2025-05-21 07:49:25] [INFO] objwatch: Starting ObjWatch tracing.
[2025-05-21 07:49:25] [INFO] objwatch: Starting tracing.
[2025-05-21 07:49:25] [DEBUG] objwatch:    22 run __main__.main <- 
[2025-05-21 07:49:25] [DEBUG] objwatch:    10 | run __main__.SampleClass.__init__ <- '0':(type)SampleClass, '1':10
[2025-05-21 07:49:25] [DEBUG] objwatch:    11 | end __main__.SampleClass.__init__ -> None
[2025-05-21 07:49:25] [DEBUG] objwatch:    13 | run __main__.SampleClass.increment <- '0':(type)SampleClass
[2025-05-21 07:49:25] [DEBUG] objwatch:    14 | | upd SampleClass.value None -> 10
[2025-05-21 07:49:25] [DEBUG] objwatch:    15 | | upd SampleClass.value 10 -> 11
[2025-05-21 07:49:25] [DEBUG] objwatch:    15 | end __main__.SampleClass.increment -> None
[2025-05-21 07:49:25] [DEBUG] objwatch:    13 | run __main__.SampleClass.increment <- '0':(type)SampleClass
[2025-05-21 07:49:25] [DEBUG] objwatch:    15 | | upd SampleClass.value 11 -> 12
[2025-05-21 07:49:25] [DEBUG] objwatch:    15 | end __main__.SampleClass.increment -> None
[2025-05-21 07:49:25] [DEBUG] objwatch:    13 | run __main__.SampleClass.increment <- '0':(type)SampleClass
[2025-05-21 07:49:25] [DEBUG] objwatch:    15 | | upd SampleClass.value 12 -> 13
[2025-05-21 07:49:25] [DEBUG] objwatch:    15 | end __main__.SampleClass.increment -> None
[2025-05-21 07:49:25] [DEBUG] objwatch:    13 | run __main__.SampleClass.increment <- '0':(type)SampleClass
[2025-05-21 07:49:25] [DEBUG] objwatch:    15 | | upd SampleClass.value 13 -> 14
[2025-05-21 07:49:25] [DEBUG] objwatch:    15 | end __main__.SampleClass.increment -> None
[2025-05-21 07:49:25] [DEBUG] objwatch:    13 | run __main__.SampleClass.increment <- '0':(type)SampleClass
[2025-05-21 07:49:25] [DEBUG] objwatch:    15 | | upd SampleClass.value 14 -> 15
[2025-05-21 07:49:26] [DEBUG] objwatch:    15 | end __main__.SampleClass.increment -> None
[2025-05-21 07:49:26] [DEBUG] objwatch:    17 | run __main__.SampleClass.decrement <- '0':(type)SampleClass
[2025-05-21 07:49:26] [DEBUG] objwatch:    19 | | upd SampleClass.value 15 -> 14
[2025-05-21 07:49:26] [DEBUG] objwatch:    19 | end __main__.SampleClass.decrement -> None
[2025-05-21 07:49:26] [DEBUG] objwatch:    17 | run __main__.SampleClass.decrement <- '0':(type)SampleClass
[2025-05-21 07:49:26] [DEBUG] objwatch:    19 | | upd SampleClass.value 14 -> 13
[2025-05-21 07:49:26] [DEBUG] objwatch:    19 | end __main__.SampleClass.decrement -> None
[2025-05-21 07:49:26] [DEBUG] objwatch:    17 | run __main__.SampleClass.decrement <- '0':(type)SampleClass
[2025-05-21 07:49:26] [DEBUG] objwatch:    19 | | upd SampleClass.value 13 -> 12
[2025-05-21 07:49:26] [DEBUG] objwatch:    19 | end __main__.SampleClass.decrement -> None
[2025-05-21 07:49:26] [DEBUG] objwatch:    26 end __main__.main -> None
[2025-05-21 07:49:26] [INFO] objwatch: Stopping ObjWatch tracing.
[2025-05-21 07:49:26] [INFO] objwatch: Stopping tracing.
```

</details>

## ⚙️ Configuration

ObjWatch offers customizable logging formats and tracing options to suit various project requirements.

### Parameters

- `targets` (list): Files, modules, classes, class members, class methods, functions, global variables, or Python objects to monitor. The specific syntax formats are as follows:
  - Module objects: Pass the module instance directly
  - Class objects: Pass the class definition directly
  - Instance methods: Pass the method instance directly
  - Function objects: Pass the function instance directly
  - String format:
    - Module: 'package.module'
    - Class: 'package.module:ClassName'
    - Class attribute: 'package.module:ClassName.attribute'
    - Class method: 'package.module:ClassName.method()'
    - Function: 'package.module:function()'
    - Global variable: 'package.module::GLOBAL_VAR'

  Example demonstrating mixed use of objects and strings:
  ```python
  from package.models import User
  from package.utils import format_str

  with objwatch.ObjWatch([
      User,                  # Directly monitor class object
      format_str,            # Directly monitor function object
      'package.config::DEBUG_MODE'  # String format global variable
  ]):
      main()
  ```
- `exclude_targets` (list, optional): Files or modules to exclude from monitoring.
- `framework` (str, optional): The multi-process framework module to use.
- `indexes` (list, optional): The indexes to track in a multi-process environment.
- `output` (str, optional): Path to a file for writing logs.
- `output_xml` (str, optional): Path to the XML file for writing structured logs. If specified, tracing information will be saved in a nested XML format for easy browsing and analysis.
- `level` (str, optional): Logging level (e.g., `logging.DEBUG`, `logging.INFO`, `force` etc.). To ensure logs are captured even if the logger is disabled or removed by external libraries, you can set `level` to "force", which will bypass standard logging handlers and use `print()` to output log messages directly to the console, ensuring that critical debugging information is not lost.
- `simple` (bool, optional): Enable simple logging mode with the format `"DEBUG: {msg}"`.
- `wrapper` (ABCWrapper, optional): Custom wrapper to extend tracing and logging functionality.
- `with_locals` (bool, optional): Enable tracing and logging of local variables within functions during their execution.
- `with_globals` (bool, optional): Enable tracing and logging of global variables across function calls. When you input the global variables in the `targets` list, you need to enable this option.

## 🪁 Advanced Usage

### Multi-Process Support

ObjWatch seamlessly integrates with multi-process applications, allowing you to monitor and trace operations across multiple processes. Specify the process indexes you wish to track using the `indexes` parameter.

Supported frameworks:
- `torch.distributed`: PyTorch's distributed environment for multi-GPU support
- `multiprocessing`: Python's built-in multiprocessing for parallel processing
- Custom frameworks: Extend support for other multi-process frameworks

```python
import objwatch

def main():
    # Your multi-process code
    pass

if __name__ == '__main__':
    obj_watch = objwatch.watch(['multi_process_module.py'], indexes=[0, 1, 2, 3], output='./mp.log', simple=False)
    main()
    obj_watch.stop()
```

#### Custom Framework Extension

ObjWatch allows you to extend support for custom multi-process frameworks by adding a `_check_init_{framework_name}` method to the MPHandls class. This method should:

1. Check if the framework is initialized
2. Set `self.initialized = True` if initialized
3. Set `self.index` to the current process index
4. Set `self.sync_fn` to a synchronization function (or None if not needed)

Example for a custom framework:

```python
class MPHandls:
    # ... existing code ...
    
    def _check_init_custom_framework(self) -> None:
        """
        Custom framework initialization check.
        Replace 'custom_framework' with your actual framework name.
        """
        try:
            import custom_framework
            if custom_framework.is_initialized():
                self.initialized = True
                self.index = custom_framework.get_current_rank()
                self.sync_fn = custom_framework.barrier
                log_info(f"custom_framework initialized. index: {self.index}")
        except ImportError:
            log_error("Custom framework not available")
            raise ValueError("Custom framework not available")
```

To use your custom framework, specify the framework name in the configuration:

```python
obj_watch = objwatch.watch(['your_module.py'], framework='custom_framework', indexes=[0, 1])
```

### Custom Wrapper Extensions

ObjWatch provides the `ABCWrapper` abstract base class, enabling users to create custom wrappers that extend and customize the library's tracing and logging capabilities. By subclassing `ABCWrapper`, developers can implement tailored behaviors that execute during function calls and returns, offering deeper insights and specialized monitoring suited to their project's specific needs.

#### ABCWrapper Class

The `ABCWrapper` class defines three essential methods that must be implemented:

- **`wrap_call(self, func_name: str, frame: FrameType) -> str`**:
  
  This method is invoked at the beginning of a function call. It receives the function name and the current frame object, which contains the execution context, including local variables and the call stack. Implement this method to extract, log, or modify information before the function executes.

- **`wrap_return(self, func_name: str, result: Any) -> str`**:
  
  This method is called upon a function's return. It receives the function name and the result returned by the function. Use this method to log, analyze, or alter information after the function has completed execution.

- **`wrap_upd(self, old_value: Any, current_value: Any) -> Tuple[str, str]`**:

  This method is triggered when a variable is updated, receiving the old value and the current value. It can be used to log changes to variables, allowing for the tracking and debugging of variable state transitions.

For more details on frame objects, refer to the [official Python documentation](https://docs.python.org/3/c-api/frame.html).

#### Supported Wrappers

The following table outlines the currently supported wrappers, each offering specialized functionality for different tracing and logging needs:

| **Wrapper**                                                         | **Description**                                                                                         |
|---------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| [**BaseWrapper**](objwatch/wrappers/base_wrapper.py)                | Implements basic logging functionality for monitoring function calls and returns.                       |
| [**CPUMemoryWrapper**](objwatch/wrappers/cpu_memory_wrapper.py)     | Uses `psutil.virtual_memory()` to retrieve CPU memory statistics. Allows selection of specific metrics for monitoring CPU memory usage during function execution. |
| [**TensorShapeWrapper**](objwatch/wrappers/tensor_shape_wrapper.py) | Logs the shapes of `torch.Tensor` objects, useful for machine learning and deep learning workflows.     |
| [**TorchMemoryWrapper**](objwatch/wrappers/torch_memory_wrapper.py) | Uses `torch.cuda.memory_stats()` to retrieve GPU memory statistics. Allows selection of specific metrics for monitoring GPU memory usage, including allocation, reservation, and freeing of memory. |

#### TensorShapeWrapper

As an example of a custom wrapper, ObjWatch includes the `TensorShapeWrapper` class within the `objwatch.wrappers` module. This wrapper automatically logs the shapes of tensors involved in function calls, which is particularly beneficial in machine learning and deep learning workflows where tensor dimensions are critical for model performance and debugging.

#### Creating and Integrating Custom Wrappers

To create a custom wrapper:

1. **Subclass `ABCWrapper`**: Define a new class that inherits from `ABCWrapper` and implement the `wrap_call`, `wrap_return` and `wrap_upd` methods to define your custom behavior.

2. **Initialize ObjWatch with the Custom Wrapper**: When initializing `ObjWatch`, pass your custom wrapper via the `wrapper` parameter. This integrates your custom tracing logic into the ObjWatch tracing process.

By leveraging custom wrappers, you can enhance ObjWatch to capture additional context, perform specialized logging, or integrate with other monitoring tools, thereby providing a more comprehensive and tailored tracing solution for your Python projects.

#### Example Use Cases

For example, the `TensorShapeWrapper` can be integrated as follows:

```python
from objwatch.wrappers import TensorShapeWrapper

# Initialize ObjWatch with the custom TensorShapeWrapper
obj_watch = objwatch.ObjWatch(['your_module.py'], simple=False, wrapper=TensorShapeWrapper))
with obj_watch:
    main()
```

## 💬 Support

If you encounter any issues or have questions, feel free to open an issue on the [ObjWatch GitHub repository](https://github.com/aeeeeeep/objwatch) or reach out via email at [aeeeeeep@proton.me](mailto:aeeeeeep@proton.me).

More usage examples can be found in the `examples` directory, which is actively being updated.

## 🙏 Acknowledgements

- Inspired by the need for better debugging and understanding tools in large Python projects.
- Powered by Python's robust tracing and logging capabilities.
