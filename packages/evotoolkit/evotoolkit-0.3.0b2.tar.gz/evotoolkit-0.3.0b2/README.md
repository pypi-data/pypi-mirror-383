# EvoToolkit

**LLM-driven solution evolutionary optimization toolkit**

EvoToolkit is a Python library that leverages Large Language Models (LLMs) to evolve solutions for optimization problems. It combines the power of evolutionary algorithms with LLM-based solution generation and refinement.

## Installation

```bash
pip install evotoolkit
```

**Note**: The package is installed as `evotoolkit` but imported as `evotool`:

```python
import evotoolkit  # Note: import name is different from package name
```

## Quick Start

```python
import evotoolkit
from evotoolkit.task.python_task.scientific_regression import ScientificRegressionTask
from evotoolkit.task.python_task import EvoEngineerPythonInterface
from evotoolkit.tools import HttpsApi

# 1. Create a task
task = ScientificRegressionTask(dataset_name="bactgrow")

# 2. Create an interface
interface = EvoEngineerPythonInterface(task)

# 3. Solve with LLM
llm_api = HttpsApi(
    api_url="https://api.openai.com/v1/chat/completions",
    key="your-api-key-here",
    model="gpt-4o"
)
result = evotoolkit.solve(
    interface=interface,
    output_path='./results',
    running_llm=llm_api,
    max_generations=5
)
```

## Features

- 🤖 **LLM-Driven Evolution**: Use language models to generate and evolve solutions
- 🔬 **Multiple Algorithms**: EoH, EvoEngineer, and FunSearch
- 🌍 **Task-Agnostic**: Supports code, text, math expressions, etc.
- 🎯 **Extensible**: Easy-to-extend task system
- 🔌 **Simple API**: High-level `evotoolkit.solve()` function

## Documentation

Full documentation: https://evotoolkit.readthedocs.io/

## License

MIT License