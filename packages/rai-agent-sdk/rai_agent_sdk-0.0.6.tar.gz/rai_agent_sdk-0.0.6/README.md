# RAI Agent SDK

A Python SDK for reviewing and updating prompts, and generating test cases for faster Copilot development.

## Features

- **Prompt Reviewer**: Review and update prompts for better AI interactions
- **Test Case Generator**: Generate comprehensive test cases from prompts
- Support for various user categories and metrics

## Installation

```bash
pip install rai-agent-sdk
```

## Usage

```python
from rai_agent_sdk import RAIAgentSDK

# Initialize the client
client = RAIAgentSDK(
    endpoint="https://func-rai-agent-eus.azurewebsites.net/api",
    credential="your-api-key"
)

# Review and update a prompt
result = client.reviewer_post({
    "prompt": "Generate a sales forecast for next quarter",
    "need_metrics": True
})

# Generate test cases
testcases = client.testcase_generator_post({
    "prompt": "Validate login functionality",
    "number_of_testcases": 3,
    "user_categories": ["Admin", "Guest"],
    "need_metrics": True
})
```

## Requirements

- Python 3.10 or higher (< 3.13)
- API subscription key for the RAI Agent service

## API Documentation

This SDK provides access to two main endpoints:

### Reviewer
- **POST /Reviewer**: Review and update prompts
- **Parameters**: 
  - `prompt` (string): The prompt to review
  - `need_metrics` (boolean): Whether to include metrics

### Test Case Generator
- **POST /Testcase_generator**: Generate test cases from prompts
- **Parameters**:
  - `prompt` (string): The prompt for test case generation
  - `number_of_testcases` (integer): Number of test cases to generate
  - `user_categories` (array): List of user categories
  - `need_metrics` (boolean): Whether to include metrics

## License

MIT License

## Author

Pavuluri Keerthika (pavulurik@maqsoftware.com)

## Support

For issues and questions, please visit: https://github.com/tanuk-824/rai_Agent