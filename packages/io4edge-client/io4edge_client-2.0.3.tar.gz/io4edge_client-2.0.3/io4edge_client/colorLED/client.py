# SPDX-License-Identifier: Apache-2.0
from io4edge_client.base.connections import ClientConnection, connectable
from io4edge_client.functionblock import Client as FbClient
import io4edge_client.api.colorLED.python.colorLED.v1alpha1.colorLED_pb2 as Pb


class Client(ClientConnection):
    """
    colorLED functionblock client.
    @param addr: address of io4edge function block (mdns name or "ip:port" address)
    @param command_timeout: timeout for commands in seconds
    """

    def __init__(self, addr: str, command_timeout=5, connect=False):
        super().__init__(FbClient(
            "_io4edge_colorLED._tcp", addr, command_timeout, connect=connect
        ))

    @connectable
    def describe(self) -> Pb.ConfigurationDescribeResponse:
        """
        Get the description from the colorLED functionblock.
        @return: description from the colorLED functionblock
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_response = Pb.ConfigurationDescribeResponse()
        self._client.describe(Pb.ConfigurationDescribe(), fs_response)
        return fs_response

    @connectable
    def set(self, channel: int, color: Pb.Color, blink: bool):
        """
        Set the state of a single output.
        @param color: color to set
        @param blink: if true the LED should blink
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlSet()
        fs_cmd.channel = channel
        fs_cmd.color = color
        fs_cmd.blink = blink
        self._client.function_control_set(fs_cmd, Pb.FunctionControlSetResponse())

    @connectable
    def get(self, channel: int) -> tuple[Pb.Color, bool]:
        """
        Get the state of a single input.
        @param color: LED color
        @param blink: if true the LED is blinking
        @raises RuntimeError: if the command fails
        @raises TimeoutError: if the command times out
        """
        fs_cmd = Pb.FunctionControlGet()
        fs_cmd.channel = channel
        fs_response = Pb.FunctionControlGetResponse()
        self._client.function_control_get(fs_cmd, fs_response)
        return fs_response.color, fs_response.blink
