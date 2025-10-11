# Client for AICosmos

This package implements the client for AICosmos. Before using this package, please make sure that you have a valid account for AICosmos. 

### AICosmosClient
By using this client, you can chat with our backend in "base" mode. To login, you will need the server's address, your username and your password. You can either start a new session, or use an existing one.

Our framework is a little bit different from "chat completions", where you give an llm the conversation history. Instead, your conversation history, along with other tool execution results, are stored in our database. This gives your a clean and simple interface to use, without worrying about constructing complicated contexts. The following code signs in to your account, and starts a new conversation in "base" mode.

```Python
from aicosmos_client.client import AICosmosClient 

# login
client = AICosmosClient(
    base_url="https://aicosmos.ai/api", username="xxx", password="xxx"
)

# create a new session
try:
    new_session_id = client.create_session()
except Exception as e:
    print(f"Error creating new session: {e}")
    exit(0)

# lookup all the sessions
try:
    my_sessions = client.get_my_sessions()
except Exception as e:
    print(f"Error getting my sessions: {e}")
    exit(0)
# [{"session_id", "title"}, ...]
print(my_sessions)

# enjoy the conversation
try:
    conversation_history = client.chat(new_session_id, "Hello")
except Exception as e:
    print(f"Error chatting: {e}")
    exit(0)
print(conversation_history)
```

Apart from "base" mode, we also support "code" mode and "lean" mode. In these modes, we provide you with a code editor, which you can open and interact with your web browser.

```Python
# enjoy the conversation
try:
    conversation_history = client.chat(
        new_session_id, "De Morgan's law. Start now.", mode="lean"
    )
except Exception as e:
    print(f"Error chatting: {e}")
    exit(0)
print(conversation_history)

# open this link with your web browser (e.g. Edge, Chrome)
url = client.get_browser_url(new_session_id)
print(url)
```

## AICosmosCLI
To show that the client is enough to build an application, we offer you an command-line interface!

```Python
from aicosmos_client.cli import AICosmosCLI

# url: https://aicosmos.ai/api
AICosmosCLI().run()
```
