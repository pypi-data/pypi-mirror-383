# Captivate AI & LLM API

## Overview
This API is developed by CaptivateChat to handle its API formats.This flexible messaging and metadata management system built using Pydantic models, designed to handle complex communication scenarios with robust type checking and validation.

## Key Components

### Models
- `ChatRequest`: Simple request model for API endpoints
- `Captivate`: Primary model managing conversation state and responses
- `CaptivateResponseModel`: Handles response messages and metadata
- `ActionModel`: Manages actions with flexible payload handling
- `ChannelMetadataModel`: Stores dynamic channel and conversation metadata

### Features
- Dynamic metadata handling
- Immutable session and chat properties
- Flexible message type support
- Custom metadata manipulation
- Conversation title management
- **File handling with text extraction and storage management**
- **Router mode with protected methods**
- **Agent escalation and routing capabilities**

You can install through:

```bash
pip install captivate-ai-api
```


## Captivate Payload

Here's the JSON payload you will send in the POST request:

```json
{
    "session_id": "lance_catcher_test_69c35e3e-7ff4-484e-8e36-792a62567b79",
    "endpoint": "action",
    "user_input": "hi man",
    "files": [
        {
            "filename": "document.pdf",
            "type": "application/pdf",
            "file": {},
            "textContent": {
                "type": "file_content",
                "text": "Extracted text content from the PDF...",
                "metadata": {
                    "source": "file_attachment",
                    "originalFileName": "document.pdf",
                    "storageType": "direct"
                }
            },
            "storage": {
                "fileKey": "uploads/1704067200000-abc123-document.pdf",
                "presignedUrl": "https://s3.amazonaws.com/bucket/uploads/1704067200000-abc123-document.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...",
                "expiresIn": 1704070800,
                "fileSize": 1024000,
                "processingTime": 15
            }
        }
    ],
    "incoming_action": [
        {
            "id": "sendEmail",
            "payload": {
                "email": "delvallelance@gmail.com",
                "message": "You are fired"
            }
        }
    ],
    "metadata": {
        "internal": {
            "channelMetadata": {
                "course_id": "abc",
                "channelMetadata": {
                    "channel": "custom-channel",
                    "channelData": {}
                },
                "user": {
                    "firstName": "Lance",
                    "lastName": "safa",
                    "email": "asdaf@gmail.com"
                },
                "phoneNumber": null,
                "custom": {
                    "mode": "non-dbfred",
                    "title": {
                        "type": "title",
                        "title": "\"Latest Updates on EU Regulations\""
                    }
                }
            }
        }
    },
    "hasLivechat": false
}
```
## API Structure

The API now has a cleaner structure with a dedicated `ChatRequest` model:

1. **`ChatRequest`**: Simple request model for API endpoints
2. **`Captivate`**: Handles both request processing and response management

This makes the API more intuitive and easier to use.


## Usage Example

### Using the new structure:

```python
from captivate_ai_api import ChatRequest, Captivate, TextMessageModel

# Create a chat request
chat_request = ChatRequest(
    session_id="test_session_123",
    user_input="Hello, how can you help me?",
    metadata={
        "internal": {
            "channelMetadata": {
                "channelMetadata": {"channel": "web"},
                "custom": {"mode": "assistant"}
            }
        }
    },
    hasLivechat=False
)

# Create Captivate instance using factory method
captivate = Captivate.create(chat_request)

# Set response messages
captivate.set_response([
    TextMessageModel(text="Hello! I'm here to help you.")
])

# Get the response
response = captivate.get_response()
```

### Factory Method Usage:

The `create()` factory method supports multiple input types:

```python
from captivate_ai_api import Captivate, TextMessageModel

# From ChatRequest (recommended)
captivate = Captivate.create(chat_request)

# From dictionary
data = {"session_id": "123", "user_input": "Hello", ...}
captivate = Captivate.create(data)

# Backward compatibility - this still works:
captivate = Captivate(**chat_request.model_dump())     # Direct constructor
```

## File Handling

The Python library receives files from the frontend (JavaScript SDK) in a comprehensive format and processes them accordingly.

### File Structure (Received from Frontend)

The frontend sends files with this structure:

```json
{
    "filename": "document.pdf",
    "type": "application/pdf",
    "file": {},
    "textContent": {
        "type": "file_content",
        "text": "Extracted text content from the PDF...",
        "metadata": {
            "source": "file_attachment",
            "originalFileName": "document.pdf",
            "storageType": "direct"
        }
    },
    "storage": {
        "fileKey": "uploads/1704067200000-abc123-document.pdf",
        "presignedUrl": "https://s3.amazonaws.com/bucket/uploads/1704067200000-abc123-document.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...",
        "expiresIn": 1704070800,
        "fileSize": 1024000,
        "processingTime": 15
    }
}
```

**Note**: This is the format sent by the Captivate Chat API JavaScript SDK. The Python library receives and processes this complete structure.

### File Processing Example

```python
from captivate_ai_api import ChatRequest, Captivate, TextMessageModel

# Create a chat request with files (as received from frontend)
chat_request = ChatRequest(
    session_id="file_session_123",
    user_input="Please analyze these documents",
    files=[
        {
            "filename": "report.pdf",
            "type": "application/pdf",
            "file": {},
            "textContent": {
                "type": "file_content",
                "text": "Q1 2024 Financial Report\n\nRevenue: $1.2M\nExpenses: $800K\nNet Profit: $400K",
                "metadata": {
                    "source": "file_attachment",
                    "originalFileName": "report.pdf",
                    "storageType": "direct"
                }
            },
            "storage": {
                "fileKey": "uploads/1704067200000-abc123-report.pdf",
                "presignedUrl": "https://s3.amazonaws.com/bucket/uploads/1704067200000-abc123-report.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...",
                "expiresIn": 1704070800,
                "fileSize": 2048000,
                "processingTime": 25
            }
        }
    ],
    metadata={
        "internal": {
            "channelMetadata": {
                "channelMetadata": {"channel": "web"},
                "custom": {"mode": "assistant"}
            }
        }
    },
    hasLivechat=False
)

# Create Captivate instance
captivate = Captivate.create(chat_request)

# Access file information
files = captivate.get_files()
for file in files:
    print(f"File: {file.get('filename')}")
    print(f"Type: {file.get('type')}")
    print(f"Size: {file.get('storage', {}).get('fileSize')} bytes")
    print(f"Text: {file.get('textContent', {}).get('text', '')[:100]}...")

# Set response with file analysis
captivate.set_response([
    TextMessageModel(text=f"I've analyzed {len(files)} file(s) and found relevant information.")
])

# Get the response
response = captivate.get_response()
```

### File Access Methods

```python
# Get all files
files = captivate.get_files()

# Access individual file properties
for file in files:
    filename = file.get('filename')
    file_type = file.get('type')
    file_size = file.get('storage', {}).get('fileSize')
    text_content = file.get('textContent', {}).get('text')
    storage_url = file.get('storage', {}).get('presignedUrl')
    
    print(f"Processing {filename} ({file_type}, {file_size} bytes)")
    if text_content:
        print(f"Content preview: {text_content[:100]}...")
    if storage_url:
        print(f"Storage URL: {storage_url}")
```

### Download Files to Memory

```python
# Download a file to memory for processing
file_info = files[0]  # Get first file
file_stream = await captivate.download_file_to_memory(file_info)

# Process the file stream
content = file_stream.read()
print(f"Downloaded {len(content)} bytes")
```

### Legacy usage (still supported):



@app.post("/chat")
async def handle_chat(data: any):
    try:
        # Create Captivate instance using the request data
        captivate = Captivate(**data.dict())
        captivate.set_conversation_title('Lord of the rings')

        # Prepare messages
        response_messages = [
            TextMessageModel(text="Welcome to our platform!"),
            ButtonMessageModel(buttons={"title": "Learn More", "options": [{"label":"Yes","value":"Yes"}]}),
            TableMessageModel(table="<table><tr><th>Name</th><th>Age</th></tr><tr><td>Alice</td><td>30</td></tr></table>"),
            CardCollectionModel(cards=[CardMessageModel(
                text="Special Offer",
                description="Get 20% off your next purchase.",
                image_url="https://example.com/offer.png",
                link="https://example.com/deals"
            )]),
            HtmlMessageModel(html="<h2>Today's Highlights</h2><ul><li>News Item 1</li><li>News Item 2</li></ul>"),
            FileCollectionModel(files=[FileModel(type='application/pdf',url="https://example.com/manual.pdf", filename="UserManual.pdf")] ),
            {"type": "custom", "content": "This is a custom message."}
        ]
        
        # Set the response messages
        captivate.set_response(response_messages)

        # Outgoing actions Both 'payload' & 'data' works for backwards compatibliity. Moving forward it is recommended to use 'data'
        outgoing_actions = [
            ActionModel(id="navigate", payload={"url": "https://example.com"}),
            ActionModel(id="submit", data={"form_id": "1234"})
        ] 
        captivate.set_outgoing_action(outgoing_actions)

        return captivate.get_response() #Returns data to captivate platform in the correct format





```

# Expected Response from `/chat` Endpoint

When you send the POST request to the `/chat` endpoint, the response will look as follows:

```json
{
    "response": [
        {
            "type": "text",
            "text": "Welcome to our platform!"
        },
        {
            "type": "button",
            "buttons": {
                "title": "Learn More",
                "options": {
                    "label":"Yes",
                    "value":"Yes"
                }
            }
        },
        {
            "type": "table",
            "table": "<table><tr><th>Name</th><th>Age</th></tr><tr><td>Alice</td><td>30</td></tr></table>"
        },
        {
            "type": "cards",
            "text": "Special Offer",
            "description": "Get 20% off your next purchase.",
            "image_url": "https://example.com/offer.png",
            "link": "https://example.com/deals"
        },
        {
            "type": "html",
            "html": "<h2>Today's Highlights</h2><ul><li>News Item 1</li><li>News Item 2</li></ul>"
        },
        { 
        "type":"files",
        "title":"these are the files",
        "files":[{
            "type": "application/pdf",
            "url": "https://example.com/manual.pdf",
            "filename": "UserManual.pdf"
            }]
        },
        {
            "type": "alert",
            "RootModel": {
                "priority": "high",
                "message": "System maintenance scheduled."
            }
        }
    ],
    "session_id": "lance_catcher_test_69c35e3e-7ff4-484e-8e36-792a62567b79",
    "metadata": {
        "internal": {
            "channelMetadata": {
                "user": {
                    "firstName": "Lance",
                    "lastName": "safa",
                    "email": "asdaf@gmail.com"
                },
                "channelMetadata": {
                    "channel": "custom-channel",
                    "channelData": {}
                },
                "custom": {
                    "mode": "non-dbfred",
                    "title": {
                        "type": "title",
                        "title": "Lord of the rings"
                    }
                },
                "conversationCreatedAt": null,
                "conversationUpdatedAt": null
            }
        }
    },
    "outgoing_action": [
        {
            "id": "navigate",
            "payload": {
                "url": "https://example.com"
            },
            "data": {
                "url": "https://example.com"
            }
        },
        {
            "id": "submit",
            "payload": {
                "form_id": "1234"
            },
            "data": {
                "form_id": "1234"
            }
        }
    ],
    "hasLivechat": false
}
```

## Functions Overview

### 1. `create` (Factory Method)

```python
@classmethod
def create(cls, data: Union[ChatRequest, Dict[str, Any]]) -> "Captivate":
```
- **Description**: Factory method to create a Captivate instance from various input types.
- **Parameters**:
  - `data`: Either a ChatRequest instance or a dictionary containing the data
- **Returns**: `Captivate` - A new Captivate instance
- **Examples**: 
```python
# From ChatRequest
chat_request = ChatRequest(session_id="123", ...)
captivate = Captivate.create(chat_request)

# From dictionary
data = {"session_id": "123", "user_input": "Hello", ...}
captivate = Captivate.create(data)
```

### 2. `get_session_id`

```python
def get_session_id(self) -> str:
```
- **Description**: Returns the value of `session_id`.
- **Example**: 
```python
session_id = captivate_instance.get_session_id()
```

### 3. `get_user_input`

```python
def get_user_input(self) -> Optional[str]:
```
- **Description**: Returns the value of `user_input`.
- **Example**: 
```python
user_input = captivate_instance.get_user_input()
```

### 4. `get_files`

```python
def get_files(self) -> Optional[List[Dict[str, Any]]]:
```
- **Description**: Returns the list of files attached to the conversation with complete file information including text content and storage details.
- **Returns**: `Optional[List[Dict[str, Any]]]` - List of file objects with comprehensive metadata from the frontend
- **Example**: 
```python
files = captivate_instance.get_files()
if files:
    for file in files:
        filename = file.get('filename')
        file_type = file.get('type')
        file_size = file.get('storage', {}).get('fileSize')
        text_content = file.get('textContent', {}).get('text')
        print(f"File: {filename} ({file_type}, {file_size} bytes)")
        if text_content:
            print(f"Content: {text_content[:100]}...")
```

### 5. `set_conversation_title`

```python
def set_conversation_title(self, title: str):
```
- **Description**: Sets the conversation title in the custom metadata.
- **Example**: 
```python
captivate_instance.set_conversation_title("New Conversation Title")
```

### 6. `get_conversation_title`

```python
def get_conversation_title(self) -> Optional[str]:
```
- **Description**: Retrieves the conversation title from the custom metadata.
- **Example**: 
```python
conversation_title = captivate_instance.get_conversation_title()
```

### 7. `set_metadata`

```python
def set_metadata(self, key: str, value: Any):
```
- **Description**: Sets a key-value pair in the custom metadata.
- **Example**: 
```python
captivate_instance.set_metadata("custom_key", "custom_value")
```

### 8. `get_metadata`

```python
def get_metadata(self, key: str) -> Optional[Any]:
```
- **Description**: Retrieves the value for a given key in the custom metadata.
- **Example**: 
```python
metadata_value = captivate_instance.get_metadata("custom_key")
```

### 9. `remove_metadata`

```python
def remove_metadata(self, key: str) -> bool:
```
- **Description**: Removes a key from the custom metadata.
- **Example**: 
```python
captivate_instance.remove_metadata("custom_key")
```

### 10. `get_channel`

```python
def get_channel(self) -> Optional[str]:
```
- **Description**: Retrieves the channel from the metadata.
- **Example**: 
```python
channel = captivate_instance.get_channel()
```

### 11. `get_user`

```python
def get_user(self) -> Optional[UserModel]:
```
- **Description**: Retrieves the user from the metadata.
- **Example**: 
```python
user = captivate_instance.get_user()
```

### 12. `set_user`

```python
def set_user(self, user: UserModel) -> None:
```
- **Description**: Sets the user in the metadata.
- **Example**: 
```python
captivate_instance.set_user(UserModel(firstName="John", lastName="Doe"))
```

### 13. `get_created_at`

```python
def get_created_at(self) -> Optional[str]:
```
- **Description**: Returns the `conversationCreatedAt` timestamp from the metadata.
- **Example**: 
```python
created_at = captivate_instance.get_created_at()
```

### 14. `get_updated_at`

```python
def get_updated_at(self) -> Optional[str]:
```
- **Description**: Returns the `conversationUpdatedAt` timestamp from the metadata.
- **Example**: 
```python
updated_at = captivate_instance.get_updated_at()
```

### 15. `get_has_livechat`

```python
def get_has_livechat(self) -> bool:
```
- **Description**: Returns the value of `hasLivechat`.
- **Example**: 
```python
has_livechat = captivate_instance.get_has_livechat()
```

### 16. `set_response`

```python
def set_response(self, response: List[Union[TextMessageModel, FileCollectionModel, ButtonMessageModel, TableMessageModel, CardCollectionModel, HtmlMessageModel, dict]]) -> None:
```
- **Description**: Sets the response messages in the `Captivate` instance.
- **Example**: 
```python
captivate_instance.set_response([
            TextMessageModel(text="Welcome to our platform!"),
            ButtonMessageModel(buttons={"title": "Learn More", "action": "navigate"}),
            TableMessageModel(table="<table><tr><th>Name</th><th>Age</th></tr><tr><td>Alice</td><td>30</td></tr></table>"),
            CardCollectionModel(cards=[CardMessageModel(
                text="Special Offer",
                description="Get 20% off your next purchase.",
                image_url="https://example.com/offer.png",
                link="https://example.com/deals"
            )]),
            HtmlMessageModel(html="<h2>Today's Highlights</h2><ul><li>News Item 1</li><li>News Item 2</li></ul>"),
           FileCollectionModel(title="See files below", files=[FileModel(type='application/pdf',url="https://example.com/manual.pdf", filename="UserManual.pdf")] ),
            {"type": "custom", "content": "This is a custom message."}
            ])
```

### 17. `get_incoming_action`

```python
def get_incoming_action(self) -> Optional[List[ActionModel]]:
```
- **Description**: Retrieves the incoming actions from the response object, if present.
- **Example**: 
```python
incoming_actions = captivate_instance.get_incoming_action()
```

### 18. `set_outgoing_action`

```python
def set_outgoing_action(self, actions: List[ActionModel]) -> None:
```
- **Description**: Sets the outgoing actions in the response object.
- **Example**: 
```python
captivate_instance.set_outgoing_action([
    ActionModel(id="navigate", data={"url": "https://example.com"})
])
```

### 19. `get_response`

```python
def get_response(self) -> Optional[str]:
```
- **Description**: Returns the `CaptivateResponseModel` as a JSON string if it exists, otherwise returns `None`.
- **Example**: 
```python
response_json = captivate_instance.get_response()
```

**Note**: The `model_dump()` method still works on both `ChatRequest` and `Captivate` instances for backward compatibility:
```python
# Both of these work identically:
captivate = Captivate.create(chat_request)                    # Factory method (recommended)
captivate = Captivate(**chat_request.model_dump())           # Direct constructor (backward compatibility)
```

### 19. `async_send_message`

```python
async def async_send_message(self, environment: str = "dev") -> Dict[str, Any]:
```
- **Description**: The async_send_message method is an asynchronous function that sends the conversation data (including messages and actions) to the captivate async messsage API endpoint, depending on the environment (dev or prod)
- **Example**: 
```python
# Create an instance of Captivate
captivate = Captivate(session_id="12345", hasLivechat=True, metadata=metadata)

# Set a message and actions
captivate.set_response([TextMessageModel(text="Hello, World!")])

# Send the message to the API in 'dev' environment
response = await captivate.async_send_message(environment="dev")
```
### 20. `download_file_to_memory`

```python
 async def download_file_to_memory(self, file_info: Dict[str, Any]) -> io.BytesIO:
```
- **Description**:  Downloads a file from the given dictionary and stores it in memory.

- **Example**: 
```python
captivate_instance.download_file_to_memory(file_info)
```

### 21. `escalate_to_human`

```python
def escalate_to_human(self) -> None:
```
- **Description**: Sets an outgoing action to escalate the conversation to a human agent.
- **Example**: 
```python
captivate_instance.escalate_to_human()
```

### 22. `escalate_to_agent_router`

```python
def escalate_to_agent_router(self, reason: Optional[str] = None, intent: Optional[str] = None, recommended_agents: Optional[List[str]] = None) -> None:
```
- **Description**: Sets an outgoing action to escalate the conversation to an agent router with optional payload data.
- **Parameters**:
  - `reason` (str, optional): The reason for escalation
  - `intent` (str, optional): The user's intent
  - `recommended_agents` (List[str], optional): Array of agent IDs to recommend
- **Example**: 
```python
# Basic escalation without payload
captivate_instance.escalate_to_agent_router()

# Escalation with all parameters
captivate_instance.escalate_to_agent_router(
    reason="Complex billing inquiry",
    intent="resolve_payment_issue", 
    recommended_agents=["agent_123", "agent_456", "agent_789"]
)
```

### 23. Router Mode Management

The Captivate class includes router mode functionality that controls access to certain methods using a decorator pattern.

#### 23.1 `enable_router_mode`

```python
def enable_router_mode(self) -> None:
```
- **Description**: Enables router mode which allows access to protected methods.
- **Example**: 
```python
captivate_instance.enable_router_mode()
```

#### 23.2 `disable_router_mode`

```python
def disable_router_mode(self) -> None:
```
- **Description**: Disables router mode, preventing access to protected methods.
- **Example**: 
```python
captivate_instance.disable_router_mode()
```

#### 23.3 `is_router_mode`

```python
def is_router_mode(self) -> bool:
```
- **Description**: Checks if router mode is currently enabled.
- **Returns**: `bool` - True if router mode is enabled, False otherwise
- **Example**: 
```python
if captivate_instance.is_router_mode():
    print("Router mode is enabled")
```

### 24. Protected Methods (Router Mode Required)

The following methods are protected by the `@requires_router_mode` decorator and can only be accessed when router mode is enabled:

#### 24.1 `set_agents`

```python
@requires_router_mode
def set_agents(self, agents_list: List[str]) -> None:
```
- **Description**: Sets the agents_list in custom metadata. This can only be set once and requires router mode to be enabled.
- **Parameters**:
  - `agents_list` (List[str]): List of agent IDs to set as agents_list
- **Example**: 
```python
# Enable router mode first
captivate_instance.enable_router_mode()

# Set agents list
captivate_instance.set_agents(["agent_001", "agent_002", "agent_003"])
```

#### 24.2 `get_outgoing_action`

```python
@requires_router_mode
def get_outgoing_action(self) -> Optional[List[ActionModel]]:
```
- **Description**: Retrieves the outgoing actions from the response object. Only available when router mode is enabled.
- **Returns**: `Optional[List[ActionModel]]` - List of outgoing actions or None
- **Example**: 
```python
# Enable router mode first
captivate_instance.enable_router_mode()

# Get outgoing actions
outgoing_actions = captivate_instance.get_outgoing_action()
```

#### 24.3 `is_escalating_to_agent_router`

```python
@requires_router_mode
def is_escalating_to_agent_router(self) -> Optional[Dict[str, Any]]:
```
- **Description**: Checks if the outgoing action is escalating to agent router and returns the payload. Only available when router mode is enabled.
- **Returns**: `Optional[Dict[str, Any]]` - The payload if escalating to agent router, None otherwise
- **Example**: 
```python
# Enable router mode first
captivate_instance.enable_router_mode()

# Check if escalating to agent router
payload = captivate_instance.is_escalating_to_agent_router()
if payload:
    print(f"Escalating with payload: {payload}")
```

### 25. Router Mode Usage Examples

#### Complete Router Mode Workflow

```python
# 1. Create Captivate instance
captivate_instance = Captivate(**data)

# 2. Router mode is disabled by default
print(captivate_instance.is_router_mode())  # False

# 3. Protected methods will fail when router mode is disabled
try:
    captivate_instance.set_agents(["agent_001"])
except ValueError as e:
    print(e)  # "set_agents is only available when router mode is enabled."

# 4. Enable router mode
captivate_instance.enable_router_mode()
print(captivate_instance.is_router_mode())  # True

# 5. Now protected methods work
captivate_instance.set_agents(["agent_001", "agent_002"])
agents = captivate_instance.get_agents()  # ["agent_001", "agent_002"]

# 6. Set up escalation
captivate_instance.escalate_to_agent_router(
    reason="Technical issue",
    recommended_agents=["agent_001"]
)

# 7. Check escalation status
payload = captivate_instance.is_escalating_to_agent_router()
print(payload)  # {"reason": "Technical issue", "recommended_agents": ["agent_001"]}

# 8. Disable router mode
captivate_instance.disable_router_mode()

# 9. Protected methods fail again
try:
    captivate_instance.get_outgoing_action()
except ValueError as e:
    print(e)  # "get_outgoing_action is only available when router mode is enabled."
```

#### Error Handling

```python
# All protected methods throw consistent errors when router mode is disabled
try:
    captivate_instance.set_agents(["agent_001"])
except ValueError as e:
    print(e)  # "set_agents is only available when router mode is enabled."

try:
    captivate_instance.get_outgoing_action()
except ValueError as e:
    print(e)  # "get_outgoing_action is only available when router mode is enabled."

try:
    captivate_instance.is_escalating_to_agent_router()
except ValueError as e:
    print(e)  # "is_escalating_to_agent_router is only available when router mode is enabled."
```

### 26. Decorator Pattern Implementation

The router mode functionality uses a decorator pattern for clean, maintainable code:

```python
def requires_router_mode(func):
    """Decorator to ensure router mode is enabled for specific methods."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._router_mode:
            raise ValueError(f"{func.__name__} is only available when router mode is enabled.")
        return func(self, *args, **kwargs)
    return wrapper
```

**Benefits of the decorator pattern:**
- **DRY Principle**: Single decorator handles all router mode checks
- **Clean Code**: Methods focus on core logic, validation is automatic
- **Easy to Extend**: Add `@requires_router_mode` to any new method
- **Consistent Errors**: Same error format across all protected methods

### 27. `escalate_to_agent`

```python
def escalate_to_agent(self, agent_id: str, reason: Optional[str] = None) -> None:
```
- **Description**: Sets an outgoing action to force redirect the conversation to a specific agent.
- **Parameters**:
  - `agent_id` (str): The ID of the agent to redirect to
  - `reason` (str, optional): The reason for the force redirection
- **Example**: 
```python
# Force redirect to a specific agent without reason
captivate_instance.escalate_to_agent("agent_123")

# Force redirect to a specific agent with reason
captivate_instance.escalate_to_agent(
    agent_id="billing_specialist_001", 
    reason="User has complex billing inquiry requiring specialist knowledge"
)
```

### 28. `set_private_metadata` and Private Metadata Usage

```python
def set_private_metadata(self, key: str, value: Any) -> None:
```
- **Description**:  
  Sets a key-value pair in the private metadata section (`custom['private']`) of the conversation. This data is for internal use and is not exposed to the end user.  
  You can retrieve this value using `get_metadata(key)`.

- **Example**:
```python


captivate_instance = Captivate(**data_action)

# Set a private metadata key-value pair
captivate_instance.set_private_metadata('my_secret', 123)

# Retrieve the private metadata value
print(captivate_instance.get_metadata('my_secret'))  # Output: 123
```

#### Reserved Key Protection

Attempting to set reserved keys like `"private"`, `"title"`, or `"conversation_title"` in metadata will raise an exception:

```python
try:
    captivate_instance.set_metadata('private', 'should fail')
except Exception as e:
    print('Expected error for reserved key:', e)
```






