from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
app = FastAPI()

# TEST METHODS

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)

# ORCHESTRATOR API
@app.post("/enqueue-test")
async def enqueue_test():
    return {"message": "Hello World"}

@app.get("/get-tests")
async def get_tests():
    return {"message": "Hello World"}

@app.get("/read-results")
async def get_results():
    return {"message": "Hello World"}

@app.get("/get-backup")
async def get_backup():
    return {"message": "Hello World"}

@app.delete("/delete-test")
async def delete_test():
    return {"message": "Hello World"}

@app.post("/stop-test")
async def stop_test():
    return {"message": "Hello World"}

@app.post("/start-test")
async def start_test():
    return {"message": "Hello World"}

# WORKER API

@app.get("/get-test")
async def get_test():
    return {"message": "Hello World"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
