import os
import base64
import io
from pathlib import Path
from typing import Union, BinaryIO
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "audio_stream_player",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("audio_stream_player", path=build_dir)


def _process_audio_data(data: Union[str, Path, bytes, BinaryIO]) -> str:
    """Convert various audio data formats to a URL or data URI.
    
    Parameters
    ----------
    data : str, Path, bytes, BytesIO, or file
        Audio data in various formats
        
    Returns
    -------
    str
        URL or data URI for the audio
    """
    # If it's a string, check if it's a URL or file path
    if isinstance(data, str):
        if data.startswith(("http://", "https://", "data:")):
            return data
        else:
            # Treat as file path
            data = Path(data)
    
    # Handle Path objects
    if isinstance(data, Path):
        with open(data, "rb") as f:
            audio_bytes = f.read()
        # Determine MIME type from extension
        ext = data.suffix.lower()
        mime_type = {
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".m4a": "audio/mp4",
            ".webm": "audio/webm",
        }.get(ext, "audio/mpeg")
        encoded = base64.b64encode(audio_bytes).decode()
        return f"data:{mime_type};base64,{encoded}"
    
    # Handle bytes
    if isinstance(data, bytes):
        encoded = base64.b64encode(data).decode()
        return f"data:audio/mpeg;base64,{encoded}"
    
    # Handle BytesIO and file-like objects
    if isinstance(data, io.BytesIO) or hasattr(data, "read"):
        if hasattr(data, "seek"):
            data.seek(0)
        audio_bytes = data.read()
        encoded = base64.b64encode(audio_bytes).decode()
        return f"data:audio/mpeg;base64,{encoded}"

    
    raise ValueError(
        f"Unsupported data type: {type(data)}. "
        "Supported types are: str (URL or file path), Path, bytes, BytesIO, or file objects."
    )


def audio_bar(
    data: Union[str, Path, bytes, BinaryIO],
    key=None,
    prime_color: str = "#3b82f6",
    second_color: str = "#f1f5f9",
):
    """Display an audio player with bar visualizer and animated state transitions.

    State automatically switches based on audio playback:
    - thinking: Audio loading (pulsing animation)
    - speaking: Audio playing (frequency visualization)
    - initializing: Audio ended (bars reset)

    Parameters
    ----------
    data : str, Path, bytes, BytesIO, or file
        Audio data in various formats:
        - str: URL (http://, https://) or file path
        - Path: pathlib.Path object pointing to an audio file
        - bytes: Raw audio data bytes
        - BytesIO: Audio data in a BytesIO object
        - file: File-like object with read() method
    key : str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    prime_color : str, optional
        Color of the visualizer bars. Default: "#3b82f6" (blue)
        Accepts hex, rgb, or named colors
    second_color : str, optional
        Background color of the visualizer. Default: "#f1f5f9" (light gray)
        Accepts hex, rgb, or named colors

    Returns
    -------
    str
        The current state of the component

    Examples
    --------
    >>> # Basic usage
    >>> audio_bar(data="audio.mp3")
    >>> 
    >>> # Custom colors
    >>> audio_bar(
    ...     data="https://example.com/stream.mp3",
    ...     prime_color="#ff6b6b",
    ...     second_color="#1a1a2e"
    ... )
    """
    # Process the audio data to get a URL or data URI
    stream_url = _process_audio_data(data)
    
    component_value = _component_func(
        mode="bar",
        state="auto",
        barCount=20,
        minHeight=15,
        maxHeight=90,
        centerAlign=True,
        streamUrl=stream_url,
        barColor=prime_color,
        backgroundColor=second_color,
        orbColors=["#CADCFC", "#A0B9D1"],
        orbSeed=1000,
        key=key,
        default="auto",
    )
    return component_value


def audio_orb(
    data: Union[str, Path, bytes, BinaryIO],
    key=None,
    prime_color: str = "#CADCFC",
    second_color: str = "#A0B9D1",
    seed: int = 1000,
):
    """Display an audio player with animated orb/blob visualizer.

    State automatically switches based on audio playback:
    - listening: Slow morphing - 還沒獲取到首包音檔 (audio loading)
    - talking: Fast morphing - 播放使用中 (audio playing)
    - idle: Very slow morphing - 播放完畢 (audio ended or idle)

    Parameters
    ----------
    data : str, Path, bytes, BytesIO, or file
        Audio data in various formats:
        - str: URL (http://, https://) or file path
        - Path: pathlib.Path object pointing to an audio file
        - bytes: Raw audio data bytes
        - BytesIO: Audio data in a BytesIO object
        - file: File-like object with read() method
    key : str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    prime_color : str, optional
        First gradient color for the orb. Default: "#CADCFC"
        Accepts hex, rgb, or named colors
    second_color : str, optional
        Second gradient color for the orb. Default: "#A0B9D1"
        Accepts hex, rgb, or named colors
    seed : int, optional
        Random seed for orb shape generation. Default: 1000
        Different seeds produce different blob shapes

    Returns
    -------
    str
        The current state of the component

    Examples
    --------
    >>> # Basic usage
    >>> audio_orb(data="audio.mp3")
    >>> 
    >>> # Custom gradient and shape
    >>> audio_orb(
    ...     data="https://example.com/stream.mp3",
    ...     prime_color="#F6E7D8",
    ...     second_color="#E0CFC2",
    ...     seed=2000
    ... )
    """
    # Process the audio data to get a URL or data URI
    stream_url = _process_audio_data(data)
    
    component_value = _component_func(
        mode="orb",
        state="auto",
        barCount=20,
        minHeight=15,
        maxHeight=90,
        centerAlign=True,
        streamUrl=stream_url,
        barColor="#3b82f6",
        backgroundColor="#f1f5f9",
        orbColors=[prime_color, second_color],
        orbSeed=seed,
        key=key,
        default="auto",
    )
    return component_value


__all__ = ["audio_bar", "audio_orb"]

