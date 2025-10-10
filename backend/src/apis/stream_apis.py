import threading
import time
from typing import Dict

from adbutils import AdbClient
from flask import Blueprint, request
from flask_socketio import SocketIO, emit

stream_bp = Blueprint("stream_bp", __name__)

# Stream configuration
STREAM_BIT_RATE = (
    2500000  # 2.5 Mbps - balanced for live monitoring (lower latency, good quality)
)
STREAM_TIME_LIMIT = 180  # 3 minutes

# Track active streams: {session_id: {'device_id': str, 'thread': Thread, 'stop_flag': bool}}
active_streams: Dict[str, dict] = {}
active_streams_lock = threading.Lock()


def init_stream_handlers(socketio: SocketIO):
    """
    Initialize Socket.IO event handlers for screen streaming.
    Must be called after SocketIO is initialized in main.py
    """

    @socketio.on("connect")
    def handle_connect():
        print(f"Client connected: {request.sid}")

    @socketio.on("disconnect")
    def handle_disconnect():
        print(f"Client disconnected: {request.sid}")
        # Stop any active streams for this session
        stop_stream_for_session(request.sid)

    @socketio.on("start_stream")
    def handle_start_stream(data):
        """
        Start streaming device screen via H.264
        Expected data: {'device_id': 'emulator-5554'}
        """
        session_id = request.sid
        device_id = data.get("device_id")

        if not device_id:
            emit("stream_error", {"error": "device_id is required"})
            return

        print(f"Starting stream for device {device_id} (session: {session_id})")

        # Check if this session already has an active stream
        with active_streams_lock:
            if session_id in active_streams:
                emit(
                    "stream_error",
                    {"error": "Stream already active for this session"},
                )
                return

        # Start streaming in background thread
        try:
            stream_thread = threading.Thread(
                target=stream_screen,
                args=(socketio, session_id, device_id),
                daemon=True,
            )

            with active_streams_lock:
                active_streams[session_id] = {
                    "device_id": device_id,
                    "thread": stream_thread,
                    "stop_flag": False,
                }

            stream_thread.start()
            emit("stream_started", {"device_id": device_id})

        except Exception as e:
            print(f"Error starting stream: {e}")
            emit("stream_error", {"error": str(e)})

    @socketio.on("stop_stream")
    def handle_stop_stream():
        """Stop streaming for current session"""
        session_id = request.sid
        print(f"Stopping stream for session: {session_id}")
        stop_stream_for_session(session_id)
        emit("stream_stopped", {})


def stop_stream_for_session(session_id: str):
    """Stop active stream for a given session"""
    with active_streams_lock:
        if session_id in active_streams:
            active_streams[session_id]["stop_flag"] = True
            # Wait for thread to finish (with timeout)
            thread = active_streams[session_id]["thread"]
            if thread.is_alive():
                thread.join(timeout=2.0)
            del active_streams[session_id]
            print(f"Stream stopped for session: {session_id}")


def is_nal_start(data: bytes, pos: int) -> bool:
    """
    Check if position in data is start of NAL unit (H.264)
    NAL units start with 0x00 0x00 0x00 0x01 or 0x00 0x00 0x01
    """
    if pos + 3 < len(data):
        if data[pos : pos + 4] == b"\x00\x00\x00\x01":
            return True
    if pos + 2 < len(data):
        if data[pos : pos + 3] == b"\x00\x00\x01":
            return True
    return False


def stream_screen(socketio: SocketIO, session_id: str, device_id: str):
    """
    Stream device screen using raw H.264 format with NAL unit detection.
    Runs in background thread.
    """
    connection = None

    try:
        print(f"Starting screenrecord for device: {device_id}")

        # Connect to device using adbutils
        adb = AdbClient(host="127.0.0.1", port=5037)
        device = adb.device(serial=device_id)

        # Use shell with stream=True to get raw H.264 stream
        connection = device.shell(
            f"screenrecord --output-format=h264 --bit-rate={STREAM_BIT_RATE} --time-limit={STREAM_TIME_LIMIT} -",
            stream=True,
        )

        print(f"Screenrecord stream started for device: {device_id}")

        # Buffer for accumulating H.264 data
        buffer = bytearray()
        chunks_sent = 0
        read_size = 4096  # Read 4KB at a time

        def should_stop():
            """Check if we should stop streaming"""
            with active_streams_lock:
                if session_id not in active_streams:
                    return True
                if active_streams[session_id]["stop_flag"]:
                    return True
            return False

        while True:
            # Check stop flag before reading
            if should_stop():
                print(f"Stop requested for session {session_id}, ending stream")
                break

            # Read data from adbutils connection
            try:
                data = connection.read(read_size)

                if not data:
                    # No more data - stream might be ending
                    print(f"[Stream {session_id}] No more data from screenrecord")
                    break

                # Add data to buffer
                buffer.extend(data)

                # Look for NAL unit boundaries in buffer
                # Search from position 1 to avoid splitting on the first NAL
                search_start = max(1, len(buffer) - len(data) - 4)

                for i in range(search_start, len(buffer)):
                    if is_nal_start(buffer, i):
                        # Found NAL unit boundary - send chunk up to this point
                        chunk_to_send = bytes(buffer[:i])

                        if len(chunk_to_send) > 0:
                            # Check stop flag before encoding
                            if should_stop():
                                print(
                                    f"[Stream {session_id}] Stop requested, ending stream"
                                )
                                break

                            # Emit to specific session
                            socketio.emit(
                                "stream_data", {"chunk": chunk_to_send}, room=session_id
                            )
                            chunks_sent += 1

                            if chunks_sent % 10 == 0:
                                print(
                                    f"[Stream {session_id}] Sent {chunks_sent} NAL units ({len(chunk_to_send)} bytes)"
                                )

                        # Remove sent data from buffer
                        buffer = buffer[i:]
                        break

                # Prevent buffer from growing too large if no NAL boundaries found
                # (this shouldn't happen with valid H.264 stream)
                if len(buffer) > 1024 * 1024:  # 1MB limit
                    print(
                        f"[Stream {session_id}] Buffer too large ({len(buffer)} bytes), flushing"
                    )
                    chunk_to_send = bytes(buffer)
                    socketio.emit(
                        "stream_data", {"chunk": chunk_to_send}, room=session_id
                    )
                    chunks_sent += 1
                    buffer.clear()

            except Exception as read_error:
                print(
                    f"[Stream {session_id}] Error reading from connection: {read_error}"
                )
                if (
                    "closed" in str(read_error).lower()
                    or "connection" in str(read_error).lower()
                ):
                    break
                time.sleep(0.1)

    except Exception as e:
        print(f"Stream error for device {device_id}: {e}")
        socketio.emit("stream_error", {"error": str(e)}, room=session_id)

    finally:
        # Cleanup - close the adbutils connection
        if connection:
            try:
                print(f"[Stream {session_id}] Closing adbutils connection")
                connection.close()
            except Exception as e:
                print(f"[Stream {session_id}] Error closing connection: {e}")

        print(
            f"[Stream {session_id}] Stream ended for device: {device_id} (total chunks sent: {chunks_sent if 'chunks_sent' in locals() else 0})"
        )
        socketio.emit("stream_ended", {}, room=session_id)

        # Remove from active streams
        with active_streams_lock:
            if session_id in active_streams:
                del active_streams[session_id]
