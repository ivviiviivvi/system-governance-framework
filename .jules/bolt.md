## 2024-05-23 - Batch Process Creation Optimization
**Learning:** Shell scripts iterating over arrays to perform external command operations (like `yq`) incur significant overhead due to repeated process creation.
**Action:** When possible, construct the data payload in memory (e.g., as a JSON string) and pass it to a single invocation of the external tool to reduce execution time and system resource usage.
