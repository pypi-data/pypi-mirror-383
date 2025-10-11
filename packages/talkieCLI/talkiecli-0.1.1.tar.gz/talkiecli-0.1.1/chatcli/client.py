# import socket
import json
import asyncio

client_list = {}  # writer -> username

async def tcp_client():
    reader, writer = await asyncio.open_connection ('127.0.0.1', 65431)

    username = input("Login with a username :")
    print("ready to chat\n")

    login_msg = {"type" : "login", "user": username}
    writer.write(json.dumps(login_msg).encode())
    await writer.drain()

    async def listen():
        while True:
            data = await reader.read(1024)
            if not data:
                break
            try:
                msg = json.loads(data.decode())
                print(f"\n{msg['user']} : {msg['message']}")
            except Exception as e:
                print("Error reading message:", e)

    asyncio.create_task(listen())

    while True:
        msg_text = await asyncio.to_thread(input, "")
        msg_dict = {"message" : msg_text, "user" : username, "type" : "text"}
        writer.write(json.dumps(msg_dict).encode())
        await writer.drain()

        if msg_text == "/exit":
            print("Exiting the chat...")
            break
    writer.close()
    await writer.wait_closed()

def main():  # synchronous entry point for pyproject.toml
    asyncio.run(tcp_client())

if __name__ == "__main__":
    main()
