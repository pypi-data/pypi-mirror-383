# Agentbase

Types:

```python
from agentbase.types import RunAgentResponse
```

Methods:

- <code title="post /">client.<a href="./src/agentbase/_client.py">run_agent</a>(\*\*<a href="src/agentbase/types/client_run_agent_params.py">params</a>) -> str</code>

# GetMessages

Types:

```python
from agentbase.types import GetMessageRetrieveResponse
```

Methods:

- <code title="post /get-messages">client.get_messages.<a href="./src/agentbase/resources/get_messages.py">retrieve</a>(\*\*<a href="src/agentbase/types/get_message_retrieve_params.py">params</a>) -> <a href="./src/agentbase/types/get_message_retrieve_response.py">GetMessageRetrieveResponse</a></code>

# ClearMessages

Types:

```python
from agentbase.types import ClearMessageClearResponse
```

Methods:

- <code title="post /clear-messages">client.clear_messages.<a href="./src/agentbase/resources/clear_messages.py">clear</a>(\*\*<a href="src/agentbase/types/clear_message_clear_params.py">params</a>) -> <a href="./src/agentbase/types/clear_message_clear_response.py">ClearMessageClearResponse</a></code>
