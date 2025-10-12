# sparq Client

Python client library for the sparq API - automated degree planning for SJSU students.

## Installation

```bash
pip install sparq
```

## Quick Start

### 1. Get Your API Key

First, run the authentication script to register and get your API key:

```bash
python auth.py
```

This will:
- Send a verification code to your email
- Generate your API key after verification
- Save it to `~/.sparq/config.txt`

### 2. Generate a Degree Plan

Use the example script to test the API:

```bash
python sparq.py
```

Or use it in your own code:

```python
from sparq import Sparq

# Initialize with your API key (automatically loaded from config)
client = Sparq()

# Generate a degree plan
plan = client.plan(
    major="Computer Science",
    cc_courses=[
        {
            "code": "COMSC 075",
            "title": "Computer Science I",
            "grade": "A",
            "institution": "Evergreen Valley College"
        }
    ],
    units_per_semester=15
)

print(plan)
```

### 3. Check Your API Usage

View your API usage statistics:

```bash
python usage.py
```

### 4. Recover Lost API Key

If you lose your API key:

```bash
python recover.py
```

## Features

- **Degree Planning**: Generate semester-by-semester plans for SJSU majors
- **Transfer Credit**: Support for community college and AP credits  
- **Usage Tracking**: Monitor your API calls and history
- **API Key Recovery**: Recover lost API keys via email verification

## Support

For issues or questions, visit: https://github.com/shiventi/sparq
