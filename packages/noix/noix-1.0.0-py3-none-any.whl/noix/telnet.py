import telnetlib3
import re


async def telnet_send_command(
    command: str, host: str, port: int, username: str = None, password: str = None
) -> None | list[str]:
    reader, writer = await telnetlib3.open_connection(host, port)

    if username is not None:
        writer.write(f"USERNAME {username}\n")
        response = str(await reader.readline()).strip()
        if response != "OK\n":
            AssertionError(f"Authentication failed. Server responded: {response}")

    if password is not None:
        writer.write(f"PASSWORD {password}\n")
        response = str(await reader.readline()).strip()
        if response != "OK\n":
            AssertionError(f"Authentication failed. Server responded: {response}")

    writer.writelines(f"{command}\n")
    response = str(await reader.readline())

    r = re.compile("^ERR (.+)$")
    if r.match(response):
        raise AssertionError(response)

    if not re.match("^BEGIN (.+)$", response):
        return [response]

    response = [response]
    while not re.match("^END (.+)$", response[len(response) - 1]):
        line = await reader.readline()
        response.append(str(line).strip())

    reader.feed_eof()
    writer.close()

    return response
