# This file is part of the project mb-netmgmt
#
# (C) 2022 Deutsche Telekom AG
#
# Deutsche Telekom AG and all other contributors / copyright
# owners license this file to you under the terms of the GPL-2.0:
#
# mb-netmgmt is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# mb-netmgmt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mb-netmgmt. If not, see <https://www.gnu.org/licenses/

import re
from socketserver import BaseRequestHandler
from socketserver import ThreadingTCPServer as Server

import paramiko

from mb_netmgmt.__main__ import Protocol, get_cli_patterns

stopped = False


class ParamikoServer(paramiko.ServerInterface):
    def __init__(self):
        self.username = None
        self.password = None

    def get_allowed_auths(*args):
        return "password,publickey"

    def check_auth_password(self, username, password):
        self.username = username
        self.password = password
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_publickey(self, username, key):
        self.username = username
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(*args):
        return paramiko.OPEN_SUCCEEDED

    def check_channel_pty_request(
        self, channel, term, width, height, pixelwidth, pixelheight, modes
    ):
        transport = channel.transport
        channel.upstream = open_upstream(
            transport.to,
            transport.key_filename,
            term,
            width,
            height,
            pixelwidth,
            pixelheight,
            self.username,
            self.password,
        )
        channel.command_prompt = b"#"
        channel.command_prompt = handle_prompt(self.handle_request)
        return True

    def check_channel_shell_request(*args):
        return True

    def check_channel_subsystem_request(*args):
        return True


class Handler(BaseRequestHandler, Protocol):
    def handle(self):
        self.callback_url = self.server.callback_url
        transport = start_server(
            self.request, self.get_to(), self.key_filename, self.handle_request
        )
        self.channel = transport.accept()
        while not stopped:
            request, request_id = self.read_request()
            self.handle_request(request, request_id)

    def send_upstream(self, request, request_id):
        self.channel.upstream.sendall(request["command"])

    def read_request(self):
        request = self.read_message(self.channel, [b"\n", b"\r"])
        return {"command": request.decode()}, None

    def respond(self, response, request_id):
        response = response["response"]
        self.channel.sendall(response)
        return response

    def read_proxy_response(self):
        prompt_patterns = [self.channel.command_prompt]
        prompt_patterns += get_cli_patterns()
        message = self.read_message(self.channel.upstream, prompt_patterns)
        return {"response": message.decode()}

    def read_message(self, channel, patterns):
        message = b""
        end_of_message = False
        while not end_of_message and not stopped:
            message += channel.recv(1024)
            for pattern in patterns:
                if re.findall(pattern, message):
                    end_of_message = True
                    break
        return message


def open_upstream(
    to,
    key_filename,
    term,
    width,
    height,
    pixelwidth,
    pixelheight,
    username=None,
    password=None,
):
    if not to:
        return
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect(
        to.hostname,
        to.port or paramiko.config.SSH_PORT,
        username,
        password,
        key_filename=key_filename,
        transport_factory=paramiko.Transport,
        look_for_keys=False,
    )
    return client.invoke_shell(term, width, height, pixelwidth, pixelheight)


def handle_prompt(handle_request):
    response = handle_request({"command": ""}, "")
    command_prompt = response.split("\n")[-1].encode()
    return command_prompt


def start_server(request, to, key_filename, handle_request):
    t = paramiko.Transport(request)
    t.add_server_key(paramiko.ECDSAKey.generate())
    t.add_server_key(paramiko.RSAKey.generate(4096))
    t.to = to
    t.key_filename = key_filename
    paramiko_server = ParamikoServer()
    paramiko_server.handle_request = handle_request
    t.start_server(server=paramiko_server)
    return t
