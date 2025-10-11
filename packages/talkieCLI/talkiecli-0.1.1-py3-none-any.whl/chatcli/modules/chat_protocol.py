import json

HOST_SERVER_NAME = "server"

def decode_message(data: bytes) -> dict:
    """Decodes raw bytes into a Python dictionary message."""
    return json.loads(data.decode())

def encode_message(msg_dict: dict) -> bytes:
    """Encodes a Python dictionary message into raw bytes."""
    return json.dumps(msg_dict).encode()

def create_server_message(message_text: str) -> dict:
    """Helper to create a standard server message."""
    return {"user": HOST_SERVER_NAME, "message": message_text}

def handle_incoming_message(
    msg: dict, 
    writer, 
    client_list: dict, 
    username: str
) -> tuple[bool, dict | list[tuple]]:
    """
    Processes a decoded message, handling commands or preparing for broadcast.

    Returns: 
        (should_exit: bool, response: dict or broadcast_list: list[tuple])
    """
    message_text = msg.get("message", "")
    
    if message_text == "/exit":
        return True, {}

    if message_text == "/list":
        # Command for a single client response
        user_list = ". ".join(client_list.values())
        reply = create_server_message(f"Online: {user_list}")
        # Return a single response dict
        return False, reply 

    # Default: Message to be broadcast
    print(username, " : ", message_text)
    broadcast_list = []
    
    # Prepare list of (writer, encoded_message) for broadcasting
    encoded_msg = encode_message(msg)
    for client_writer in list(client_list.keys()):
        if client_writer != writer:
            broadcast_list.append((client_writer, encoded_msg))
            
    # Return the list of (writer, data) tuples to send
    return False, broadcast_list
