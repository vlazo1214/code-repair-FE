# api/WebSocketClient.py
import asyncio
import json
import websockets
import threading

class WebSocketClient:
    def __init__(self, ws_url="ws://localhost:8000"):
        self.ws_url = ws_url
        self.websocket = None
        self.session_token = None
        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self.loop = None
    
    async def connect(self, session_token):
        """Establish WebSocket connection using session_token."""
        self.session_id = session_token
        url = f"{self.ws_url}/start-llm-session?websocket=true&session_token={session_token}"
        self.websocket = await websockets.connect(url)
        print(f"WebSocket connection established: {url}")
        return self.websocket
    
    async def disconnect(self):
        """Close the WebSocket connection."""
        self._running = False
        if self.websocket:
            await self.websocket.close()
            print("WebSocket connection closed")
            self.websocket = None
    
    def start_background_connection(self, session_token):
        """Start a background thread that maintains the WebSocket connection."""
        with self._lock:
            if self._thread and self._thread.is_alive():
                print("Background connection already running")
                return
            
            self.session_token = session_token
            self._running = True
            self._thread = threading.Thread(
                target=self._maintain_connection_thread,
                daemon=True
            )
            self._thread.start()
            print("Background WebSocket thread started")
    
    def _maintain_connection_thread(self):
        """Thread function that maintains the WebSocket connection."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        async def maintain():
            try:
                print(f"Attempting to connect to WebSocket with session_token: {self.session_token}")
                try:
                    await self.connect(self.session_token)

                    await asyncio.sleep(0.1)
                    print("WebSocket connection successful")
                    
                    while self._running:
                        try:
                            # Periodic check or heartbeat
                            await asyncio.sleep(30)
                        except Exception as e:
                            print(f"WebSocket error during maintenance: {e}")
                            # Try to reconnect
                            if self._running:
                                await asyncio.sleep(5)
                                try:
                                    await self.connect(self.session_token)
                                except Exception as reconnect_error:
                                    print(f"Reconnection failed: {reconnect_error}")
                except websockets.exceptions.InvalidStatus as status_error:
                    print(f"WebSocket connection rejected with status: {status_error}")
                    print(f"This typically means the server rejected the connection parameters.")
                    print(f"Check if the session_token '{self.session_token}' is valid and the WebSocket endpoint is correct.")
                except Exception as connect_error:
                    print(f"WebSocket connection error: {type(connect_error).__name__}: {connect_error}")
            finally:
                try:
                    await self.disconnect()
                except Exception as e:
                    print(f"Error during disconnect: {e}")

        self.loop.run_until_complete(maintain())
    

    async def send_message_async(self, content):
        """Send a message via WebSocket and return only the text content."""
        if not self.websocket:
            raise ValueError("WebSocket not connected. Call connect() first.")

        try:
            await self.websocket.send(content)
            return await self.websocket.recv()

            # print(f"Raw response: {response}")

            # if isinstance(response, bytes):
            #     response = response.decode("utf-8")

            # try:
            #     parsed_response = json.loads(response)
            #     if isinstance(parsed_response, dict) and "content" in parsed_response:  # Safer JSON handling
            #         return parsed_response["content"]
            #     else:
            #         return response  # Return the whole response if "content" is not found
            # except json.JSONDecodeError:
            #     return response

        except Exception as e:
            print(f"Error sending message: {e}")
            return None  # Consistent return value on error

    def send_message(self, content):
        """Synchronous wrapper for send_message_async with error handling."""
        if not self.loop or not self.websocket:
            raise RuntimeError("WebSocket is not connected.")

        try:
            future = asyncio.run_coroutine_threadsafe(self.send_message_async(content), self.loop)
            response = future.result() # Still blocking, but now exceptions are caught
            
            print(f"Raw response: {response}")

            if isinstance(response, bytes):
                response = response.decode("utf-8")

            try:
                parsed_response = json.loads(response)
                if isinstance(parsed_response, dict) and "content" in parsed_response:  # Safer JSON handling
                    return parsed_response["content"]
                else:
                    return response  # Return the whole response if "content" is not found
            except json.JSONDecodeError:
                return response
        except Exception as e:
            print(f"Error in send_message: {e}")
            return None  # Consistent return value

    async def cleanup(self):
        """Clean up WebSocket connection on shutdown."""
        self._running = False
        if self.websocket:
            await self.disconnect()
