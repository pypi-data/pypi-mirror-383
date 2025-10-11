import asyncio
from chatcli.modules.connection_handler import handle_client

# --- Configuration and State ---
HOST = "127.0.0.1"
PORT = 65431
# Global state for connected clients
client_list = {} 
# client_list: {writer_object: username_string}

async def start_server():
    """
    Main function to start the asyncio server.
    """
    # Use a lambda to pass the global client_list to the handler function
    server_handler = lambda r, w: handle_client(r, w, client_list)
    
    server = await asyncio.start_server(server_handler, HOST, PORT)
    print(f"Server is listening on {HOST}:{PORT}")
    
    async with server:
        await server.serve_forever()

def main():  
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\nServer shutting down.")


if __name__ == "__main__":
    main()