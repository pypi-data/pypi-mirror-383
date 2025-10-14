# SQL Agent Evaluation SDK

A Python SDK for evaluating SQL Agent accuracy with comprehensive test datasets and intelligent LLM-based scoring.

[中文文档](README_CN.md) | English

## Features

- 🎯 **Simple Interface**: Easy-to-use SQLAgent interface
- 📊 **38 Test Questions**: Covering 5 major SQL optimization scenarios
- 🤖 **LLM Scoring**: Intelligent evaluation with detailed explanations
- 📈 **Auto Reports**: Automatic result summary and detailed reports
- 🔧 **Flexible Config**: Custom database and LLM configuration

## Quick Start

### 1. Install & Configure

```bash
pip install -r requirements.txt
```

Create `config/.env`:
```env
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=your_password
DATABASE_NAME=sql_eval_test

EVAL_LLM_API_KEY=your_api_key
EVAL_LLM_BASE_URL=https://api.openai.com/v1
EVAL_LLM_MODEL=gpt-4
```

### 2. Create & Evaluate Agent

```python
import asyncio
from sqleval import SQLAgent, SQLEvaluator

class MyAgent(SQLAgent):
    def optimize(self, sql_query: str) -> str:
        # Your optimization logic here
        return "Your optimization suggestions"
    
    def get_name(self) -> str:
        return "My Agent"

async def main():
    evaluator = SQLEvaluator()
    agent = MyAgent()
    
    # Evaluate agent (automatically displays results)
    dataset_results = await evaluator.evaluate(agent, datasets=['example'])
    
    # Extract result and save report
    result = dataset_results['example'][0]
    result.save_report("reports/my_agent_report.md")

asyncio.run(main())
```

## Evaluation Datasets

| Dataset | Questions | Weight | Description |
|---------|-----------|--------|-------------|
| **index_invalidation** | 10 | 25% | Index usage issues (functions, type conversion, wildcards) |
| **rule_based_traps** | 9 | 25% | Scenarios that trap rule-based agents |
| **inefficient_join** | 10 | 20% | JOIN and subquery optimization |
| **execution_plan_issues** | 3 | 15% | Execution plan problems (statistics, parameter sniffing) |
| **access_path_issues** | 6 | 15% | Data access optimization (SELECT *, filtering) |

## Examples

- **`examples/quick_start.py`** - Minimal example to get started
- **`examples/custom_agent_example.py`** - How to create custom agents
- **`examples/batch_evaluation_example.py`** - Compare multiple agents
- **`examples/manual_environment_control.py`** - Manual environment setup and cleanup
- **`examples/reuse_dataset_example.py`** - Reuse prepared datasets for faster evaluation
- **`examples/validate_config.py`** - Validate your configuration

## API Reference

### SQLAgent Interface

```python
class MyAgent(SQLAgent):
    def optimize(self, sql_query: str) -> str:
        """Return optimization suggestions for the SQL query"""
        return "Your suggestions"
    
    def get_name(self) -> str:
        """Return agent name"""
        return "My Agent"
```

### SQLEvaluator

#### Basic Evaluation

```python
evaluator = SQLEvaluator()

# Single agent evaluation
dataset_results = await evaluator.evaluate(agent, datasets=['example'])

# Batch evaluation (compare multiple agents)
dataset_results = await evaluator.evaluate([agent1, agent2, agent3])
```

**Note**: The `evaluate` method automatically displays comparison results and saves combined reports (`*_combined_report.md`). For individual dataset reports, call `result.save_report()`.

#### Manual Environment Control

For large datasets or repeated evaluations, you can manually control environment setup and cleanup:

```python
evaluator = SQLEvaluator()

try:
    # 1. Prepare environment once (may be slow for large datasets)
    evaluator.prepare_environment(datasets=['execution_plan_issues'])
    
    # 2. Run multiple evaluations reusing the prepared environment
    await evaluator.evaluate(agent1, auto_cleanup=False)
    await evaluator.evaluate(agent2, auto_cleanup=False)
    await evaluator.evaluate(agent3, auto_cleanup=False)
    
finally:
    # 3. Clean up environment (automatically closes connection)
    evaluator.clean_environment()
```

**Benefits**:
- Significantly faster for repeated evaluations (no re-setup)
- Full control over when to clean up data
- Useful for debugging (inspect database state between runs)

## Project Structure

```
sqleval/
├── sqleval/                 # Core SDK
│   ├── core/
│   │   ├── agent.py        # SQLAgent base class
│   │   ├── evaluator.py    # SQLEvaluator main class
│   │   └── result.py       # EvaluationResult class
├── datasets/               # Evaluation datasets
│   ├── index_invalidation/ # Index usage scenarios
│   ├── rule_based_traps/   # Rule-based agent traps
│   ├── inefficient_join/   # JOIN optimization
│   ├── execution_plan_issues/ # Execution plan problems
│   ├── access_path_issues/ # Data access optimization
│   └── meta.txt           # Dataset weights
├── examples/              # Usage examples
└── reports/               # Generated reports
```

## License

Apache License 2.0 - see LICENSE file for details.