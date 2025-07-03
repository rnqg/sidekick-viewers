# Sidekick Boost Viewers

Simple script for boosting views on a webpage using multiple headless Chrome instances.

## Usage

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run:**
    ```bash
    python main.py [options]
    ```

### Options

-   `-n`, `--browsers`: Number of browser instances (default: 2)
-   `-u`, `--url`: Target URL
-   `-m`, `--min-mem`: Min free RAM in GB to launch (default: 2)

### Example

Run 10 instances on a specific URL:

```bash
python main.py -n 10 -u "https://example.com"
``` 