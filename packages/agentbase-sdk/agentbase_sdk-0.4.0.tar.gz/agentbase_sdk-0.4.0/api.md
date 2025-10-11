# Agentbase

Types:

```python
from agentbase.types import RunAgentResponse
```

Methods:

- <code title="post /">client.<a href="./src/agentbase/_client.py">run_agent</a>(\*\*<a href="src/agentbase/types/client_run_agent_params.py">params</a>) -> str</code>

# Agent

Types:

```python
from agentbase.types import AgentRunResponse
```

Methods:

- <code title="post /">client.agent.<a href="./src/agentbase/resources/agent.py">run</a>(\*\*<a href="src/agentbase/types/agent_run_params.py">params</a>) -> str</code>

# Messages

Types:

```python
from agentbase.types import MessageClearResponse, MessageGetResponse
```

Methods:

- <code title="post /clear-messages">client.messages.<a href="./src/agentbase/resources/messages.py">clear</a>(\*\*<a href="src/agentbase/types/message_clear_params.py">params</a>) -> <a href="./src/agentbase/types/message_clear_response.py">MessageClearResponse</a></code>
- <code title="post /get-messages">client.messages.<a href="./src/agentbase/resources/messages.py">get</a>(\*\*<a href="src/agentbase/types/message_get_params.py">params</a>) -> <a href="./src/agentbase/types/message_get_response.py">MessageGetResponse</a></code>
