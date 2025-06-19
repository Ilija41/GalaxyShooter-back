import asyncio
import websockets
import json

commands = {
    "yellow": {"LEFT": False, "RIGHT": False, "UP": False, "DOWN": False, "FIRE": False},
    "red":    {"LEFT": False, "RIGHT": False, "UP": False, "DOWN": False, "FIRE": False},
}

connections = {} 

async def handler(ws, path = None):
    msg = await ws.recv()
    data = json.loads(msg)
    if data.get("type") != "register" or data.get("player") not in commands:
        await ws.send(json.dumps({"error": "Morate poslati {{type: 'register', player: 'yellow'|'red'}}"}))
        return

    player = data["player"]
    if player in connections:
        await ws.send(json.dumps({"error": "Igrač već povezan"}))
        return

    connections[player] = ws
    print(f"✅ {player} se povezao kao kontroler")

    try:
        async for message in ws:
            data = json.loads(message)
            if data.get("type") == "action":
                action = data.get("action")
                state  = data.get("state")
                if action in commands[player]:
                    commands[player][action] = state
                    # debug
                    print(f"📥 {player} -> {action} = {state}")
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        del connections[player]
        print(f"❌ {player} je prekinuo vezu")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("🌐 WebSocket server sluša na ws://0.0.0.0:8765")
        await asyncio.Future() 

if __name__ == "__main__":
    asyncio.run(main())
