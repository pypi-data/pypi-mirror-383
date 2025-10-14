# Creative Catalyst API Client

[![PyPI version](https://img.shields.io/pypi/v/creative-catalyst-client.svg)](https://pypi.org/project/creative-catalyst-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/creative-catalyst-client.svg)](https://pypi.org/project/creative-catalyst-client/)

A robust Python client for interacting with the Creative Catalyst Engine API. This client handles job submission and uses a real-time Server-Sent Events (SSE) stream to provide progress updates and retrieve final results, eliminating the need for inefficient polling.

---

## Table of Contents

- [Creative Catalyst API Client](#creative-catalyst-api-client)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Configuration](#configuration)
    - [Example](#example)
  - [Error Handling](#error-handling)
  - [Development](#development)
  - [License](#license)

---

## Features

-   **Simple Interface:** A clean, intuitive client for submitting creative briefs.
-   **Real-Time & Efficient:** Uses Server-Sent Events (SSE) to get job status updates the moment they happen, with no need for manual polling.
-   **Robust Error Handling:** Includes a set of custom exceptions to handle API connection issues, job submission failures, and failed jobs gracefully.
-   **Configurable:** The target API server URL is configured via a single environment variable, making it easy to switch between development, staging, and production environments.

---

## Installation

The package is hosted on the public Python Package Index (PyPI).

```bash
pip install creative-catalyst-client
```

It is highly recommended to pin the package to a specific version in your project's `requirements.txt` file to ensure reproducible builds:

```
# In your requirements.txt
creative-catalyst-client==1.1.6
```

<details>
<summary><strong>(Alternative) Installation from Private GitHub Packages</strong></summary>

If your project requires installing from the private GitHub Packages registry, you will need a GitHub Personal Access Token (PAT) with `read:packages` scope.

1.  **Configure `pip`:** Add the following line to the top of your `requirements.txt` file, replacing `YOUR-GITHUB-USERNAME` with the correct GitHub organization or username:
    ```
    --extra-index-url https://pypi.pkg.github.com/YOUR-GITHUB-USERNAME
    ```

2.  **Set Authentication Token:** Before running `pip install`, set your PAT as an environment variable:
    ```bash
    export GITHUB_TOKEN=your_personal_access_token_here
    ```

3.  **Install:** Now, `pip install -r requirements.txt` will be able to find and download the package from the private registry.
</details>

---

## Usage

### Configuration

Ensure the following environment variable is set in the environment where you are running your application:

```
CREATIVE_CATALYST_API_URL="http://<ip_address_of_catalyst_server>:9500"
```

The client will automatically read this value.

### Example

The following is a complete example of how to submit a job and receive the final report.

The `get_creative_report_stream` method is a Python generator. You should iterate over it in a `for` loop to receive real-time status updates.


```python
from api_client.client import CreativeCatalystClient
from api_client.exceptions import APIClientError

client = CreativeCatalystClient()
creative_brief = "A new creative brief..."
final_report = None

try:
    # The new method is now iterable in a for loop.
    for update in client.get_creative_report_stream(creative_brief):

        event_type = update.get("event")

        if event_type == "job_submitted":
            print(f"Job successfully submitted with ID: {update.get('job_id')}")

        elif event_type == "progress":
            # This is a real-time progress update.
            status_message = update.get("status")
            print(f"Server progress: {status_message}")

        elif event_type == "complete":
            # This is the final, successful result.
            final_report = update.get("result")
            print("Successfully received the final report.")
            break # Exit the loop

except APIClientError as e:
    print(f"An error occurred: {e}")

# Now you can use the final report.
if final_report:
    print("\n--- Final Report Theme ---")
    print(final_report.get('final_report', {}).get('overarching_theme'))
```

---

## Error Handling

The client will raise specific exceptions for different failure modes, all inheriting from `APIClientError`. You can catch these to handle errors gracefully.

-   **`ConnectionError`**: Raised if the client cannot connect to the API server at all.
-   **`JobSubmissionError`**: Raised if the initial job submission fails (e.g., due to a server error or invalid request).
-   **`JobFailedError`**: Raised if the job is accepted but fails during processing on the worker.

---

## Development

This section is for developers contributing to the `creative-catalyst-client` package itself.

The project uses `pip-tools` for dependency management.

1.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
2.  **Install all dependencies:**
    ```bash
    pip install -r dev-requirements.txt
    ```
3.  **To add a dependency,** edit `pyproject.toml` (for production) or `dev-requirements.in` (for development).
4.  **To update the lock files,** run: `pip-compile --strip-extras dev-requirements.in`.
5.  **To build the package,** run: `python -m build`.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
