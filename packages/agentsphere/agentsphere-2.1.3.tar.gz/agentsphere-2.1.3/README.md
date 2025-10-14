## What is Agentsphere?
[Agentsphere](https://www.agentsphere.run/) is an open-source infrastructure that allows you to run AI-generated code in secure isolated sandboxes in the cloud. To start and control sandboxes, use our [JavaScript SDK](https://www.npmjs.com/package/agentsphere-js) or [Python SDK](https://pypi.org/project/agentsphere).

## Run your first Sandbox

### 1. Install SDK

```
pip install agentsphere-code-interpreter
```

### 2. Get your Agentsphere API key
1. Sign up to Agentsphere [here](https://www.agentsphere.run).
2. Get your API key [here](https://www.agentsphere.run/apikey).
3. Set environment variable with your API key
```
AGENTSPHERE_API_KEY= ***
```

### 3. Execute code with code interpreter inside Sandbox

```py
from agentsphere import Sandbox

with Sandbox.create() as sandbox:
    sandbox.run_code("x = 1")
    execution = sandbox.run_code("x+=1; x")
    print(execution.text)  # outputs 2
```

### 4. Check docs
Visit [Agentsphere documentation](https://www.agentsphere.run/docs/home).
