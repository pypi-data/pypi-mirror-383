import re
from typing import Any

from .telnet import telnet_send_command


class UpsError(IOError):
    def __init__(self, error: str):
        super().__init__(f"Unexpected response: {error}")


class NUT:
    def __init__(
        self,
        host: str,
        ups_name: str,
        port: int = 3493,
        username: str = None,
        password: str = None,
    ):
        self.host = host
        self.port = port
        self.ups_name = ups_name
        self.username = username
        self.password = password

    async def list_vars(self) -> list[str]:
        try:
            v = await telnet_send_command(
                f"LIST VAR {self.ups_name}",
                self.host,
                self.port,
                self.username,
                self.password,
            )
        except AssertionError as e:
            raise UpsError(e.args[0])

        r = re.compile(rf'^VAR {self.ups_name} (.+) "(.+)"$')
        variables = []

        for line in v:
            m = r.match(line)
            if m:
                variables.append(m.group(1))

        return variables

    async def get(self, item) -> str:
        try:
            v = await telnet_send_command(
                f"GET VAR {self.ups_name} {item}",
                self.host,
                self.port,
                self.username,
                self.password,
            )
            v = v[0]
        except AssertionError as e:
            raise UpsError(e.args[0])

        r = re.compile(rf'^VAR {self.ups_name} {item} "(.+)"$')

        return r.findall(v)[0]

    async def set(self, item: str, value: Any):
        try:
            await telnet_send_command(
                f'SET VAR {self.ups_name} {item} "{value}"',
                self.host,
                self.port,
                self.username,
                self.password,
            )
        except AssertionError as e:
            raise UpsError(e.args[0])

    async def list_commands(self) -> list[str]:
        try:
            v = await telnet_send_command(
                f"LIST CMD {self.ups_name}",
                self.host,
                self.port,
                self.username,
                self.password,
            )
        except AssertionError as e:
            raise UpsError(e.args[0])

        r = re.compile(rf"^CMD {self.ups_name} (.+)$")
        commands = []

        for line in v:
            m = r.match(line)
            if m:
                commands.append(m.group(1))

        return commands

    async def call(self, command: str):
        try:
            await telnet_send_command(
                f"INSTCMD {self.ups_name} {command}",
                self.host,
                self.port,
                self.username,
                self.password,
            )
        except AssertionError as e:
            raise UpsError(e.args[0])
