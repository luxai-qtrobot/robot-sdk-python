"""HTTP WebRTC helpers forward signaling settings and reuse them for plugins."""

from unittest.mock import MagicMock, patch

from luxai.magpie.transport.webrtc import WebRTCConnection
from luxai.robot.core import Robot


def test_http_connection_and_plugin_inherit_settings():
    robot_conn = MagicMock()
    robot_conn.connect.return_value = True
    plugin_conn = MagicMock()
    plugin_conn.connect.return_value = True
    headers = {"Authorization": "Bearer token"}
    headers_provider = lambda: {"Authorization": "Bearer refreshed"}
    options = object()

    with patch.object(WebRTCConnection, "with_http", side_effect=[robot_conn, plugin_conn]) as factory, \
         patch.object(Robot, "__init__", autospec=True, return_value=None) as init, \
         patch.object(Robot, "enable_plugin", autospec=True) as enable_plugin:
        robot = Robot.connect_webrtc_http(
            "https://relay.example/signal", "ROBOT001",
            headers=headers, headers_provider=headers_provider,
            webrtc_options=options, reconnect=True,
        )
        transport = init.call_args.kwargs["transport"]
        robot._robot_transport = transport
        robot.enable_plugin_webrtc_http("realsense-driver", "camera-node")

    assert factory.call_count == 2
    assert factory.call_args_list[0].args == ("https://relay.example/signal",)
    assert factory.call_args_list[0].kwargs["session_id"] == "ROBOT001"
    assert factory.call_args_list[1].kwargs["session_id"] == "camera-node"
    for call in factory.call_args_list:
        assert call.kwargs["headers"] is headers
        assert call.kwargs["headers_provider"] is headers_provider
        assert call.kwargs["options"] is options
        assert call.kwargs["reconnect"] is True
    enable_plugin.assert_called_once()
    assert enable_plugin.call_args.args[1] == "realsense-driver"


def test_http_connection_timeout_disconnects():
    conn = MagicMock()
    conn.connect.return_value = False
    with patch.object(WebRTCConnection, "with_http", return_value=conn):
        try:
            Robot.connect_webrtc_http("https://relay.example/signal", "ROBOT001")
        except RuntimeError as error:
            assert "timed out" in str(error)
        else:
            raise AssertionError("Expected a WebRTC handshake timeout")
    conn.disconnect.assert_called_once()
