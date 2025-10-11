# Email Octopus Python SDK
A friendly, modern Python wrapper for the [Email Octopus API v2](https://emailoctopus.com/api-documentation/v2).

## Features
- Full support for all Email Octopus API v2 endpoints.
- Intuitive methods and object-oriented design.
- Built-in handling for authentication and API errors.
- Type-hinted for a better development experience.

## Installation
You can install the library via pip:
```
pip install emailoctopus-python-sdk
```

## Usage
First, get your API key from your Email Octopus account.
```
from emailoctopus_sdk import Client
import os

# It's recommended to load your API key from an environment variable
api_key = os.environ.get("EMAILOCTOPUS_API_KEY")

if not api_key:
    raise ValueError("EMAILOCTOPUS_API_KEY environment variable not set.")

client = Client(api_key=api_key)

try:
    # Example: Get all mailing lists
    lists = client.get_all_lists()
    for lst in lists:
        print(f"List ID: {lst['id']}, Name: {lst['name']}, Subscribers: {lst['counts']['subscribed']}")

    # Example: Get a specific list
    a_specific_list_id = "YOUR_LIST_ID_HERE"
    list_details = client.get_list(a_specific_list_id)
    print(f"\nDetails for list {list_details['name']}:")
    print(list_details)

except Exception as e:
    print(f"An error occurred: {e}")
```

## Development
To set up the development environment:
1. Clone the repository: ```git clone https://github.com/dayluke/emailoctopus-python.git```
2. Create and activate a virtual environment.
3. Install dependencies: ```pip install -e .[dev]```
4. Run tests: ```pytest```

## Contributing
Contributions are welcome! Please read the [CONTRIBUTING](CONTRIBUTING.md) file for details on how to get started.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
