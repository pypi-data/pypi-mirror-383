import os
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


def audio_stream_player(
    stream_url,
    key=None,
):
    """Display an audio stream player with frequency visualization and animated state transitions.

    State automatically switches based on audio playback:
    - thinking: Audio loading
    - speaking: Audio playing
    - initializing: Audio ended

    Parameters
    ----------
    stream_url : str
        URL of an audio stream to play and visualize (required)
    key : str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    str
        The current state of the component
    """
    component_value = _component_func(
        state="auto",
        barCount=20,
        minHeight=15,
        maxHeight=90,
        centerAlign=True,
        streamUrl=stream_url,
        key=key,
        default="auto",
    )
    return component_value


__all__ = ["audio_stream_player"]

