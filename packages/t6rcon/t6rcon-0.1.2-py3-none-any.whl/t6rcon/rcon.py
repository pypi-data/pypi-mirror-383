from socket import socket, AF_INET, SOCK_DGRAM, timeout
from typing import Optional, List
import re

from .core.constants import Commands, Colors
from .core.models import Player, ServerStatus, ServerInfo
from .exceptions import PlutoRCONError, AuthenticationError, TimeoutError, InvalidResponseError

class PlutoRCON:
    def __init__(self,*, ip_addr: str, port: int, password: Optional[str] = None, timeout: int = 2) -> None:
        self.ip_adrr  = ip_addr
        self.port     = port
        self.password = password

        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.settimeout(timeout)

    def send_command(self, command: str, *, arg: Optional[str] = None, auth: bool = False) -> List[str]:
        if not auth: 
            packet = b"\xFF\xFF\xFF\xFF" + command.encode("latin1") + b"\n"
        else: 
            if not self.password:
                raise AuthenticationError("No RCON password provided for authenticated command")
            
            command = f"rcon {self.password} {command} {arg if arg else ''}"
            packet  = b"\xFF\xFF\xFF\xFF" + command.encode("latin1") + b"\n"

        try:
            self.socket.sendto(packet, (self.ip_adrr, self.port))
            data, _ = self.socket.recvfrom(4096)
            response = data.decode("latin1", errors="ignore")
            return response.strip().split("\n")
        
        except timeout: raise TimeoutError
        except Exception as e: raise PlutoRCONError(f"Unexpected error: {e}")

    def get_players(self) -> List[Player]:
        players = []

        response = self.send_command(Commands.GET_STATUS)
        if not response or not response[0].strip().endswith("statusResponse"):
            raise InvalidResponseError(command=Commands.GET_STATUS, response=response[0] if response else "<empty>")

        for player_id, line in enumerate(response[2:]):
            if not line.strip(): continue
            parts = line.split(" ", 2)
            if len(parts) < 3: continue

            score, ping, raw_name = parts
            match = re.search(r'"(.*?)"', raw_name)
            if not match: continue

            players.append(
                Player(
                    id=player_id,
                    player=match.group(1),
                    ping=int(ping),
                    score=int(score),
                )
            )

        return players

    def server_status(self) -> ServerStatus:
        status = {}

        response = self.send_command(Commands.GET_STATUS)
        if not response or not response[0].strip().endswith("statusResponse"):
            raise InvalidResponseError(command=Commands.GET_STATUS, response=response[0])
        
        data  = response[1]
        lines = data.strip("\\").split("\\")
        for i in range(0, len(lines) - 1, 2):
            k, v = lines[i], lines[i + 1]
            status[k] = v

        return ServerStatus(**status)

    def info(self) -> ServerInfo:
        info = {}
        
        response = self.send_command(Commands.GET_INFO)
        if not response or not response[0].strip().endswith("statusResponse"):
            raise InvalidResponseError(command=Commands.GET_STATUS, response=response[0])
        
        data  = response[1]
        lines = data.strip("\\").split("\\")
        for i in range(0, len(lines) - 1, 2):
            k, v = lines[i], lines[i + 1]
            info[k] = v

        return ServerInfo(**info)
    
    def status(self) -> List[Player]:
        players = []

        response = self.send_command(Commands.STATUS)
        if not response or not response[0].strip().endswith("statusResponse"):
            raise InvalidResponseError(command=Commands.STATUS, response=response[0])
        
        if len(response) <= 4:
            raise InvalidResponseError(command=Commands.STATUS, response=response[0])

        lines = response[4:]

        pattern = re.compile(
            r'(?P<num>\d+)\s+'
            r'(?P<score>-?\d+)\s+'
            r'(?P<bot>\w+)?\s*'
            r'(?P<ping>\d+|LOAD)\s+'
            r'(?P<guid>[0-9a-fA-F]+)\s+'
            r'(?P<name>.+?)\s+'
            r'(?P<lastmsg>\d+)\s+'
            r'(?P<ipport>[\d\.]+:\d+)\s+'
            r'(?P<qport>\d+)\s+'
            r'(?P<rate>\d+)'
        )

        for line in lines:
            clean_line = line.encode("ascii", errors="ignore").decode().strip()
            match = pattern.match(clean_line)
            if not match: continue

            ip, port = match.group("ipport").split(":")
            players.append(
                Player(
                    id      = int(match.group("num")),
                    player  = match.group("name"),
                    ping    = int(match.group("ping")) if match.group("ping") != "LOAD" else "LOAD",
                    score   = int(match.group("score")),
                    ip      = ip,
                    port    = int(port),
                    qport   = int(match.group("qport")),
                    guid    = match.group("guid"),
                    lastmsg = int(match.group("lastmsg")),
                    rating  = int(match.group("rate")),
                )
            )

        return players
    
    def say(self, message: str) -> bool:
        response = self.send_command(Commands.SAY, arg=f"{Colors.LBLUE}{message}", auth=True)
        if not response:
            raise InvalidResponseError(command=Commands.GET_STATUS, response=response[0])
        
        return response[0] == "ÿÿÿÿprint"
    
    def tell(self, player_id: int, message: str) -> bool:
        response = self.send_command(Commands.TELL, arg=f"{player_id} {message}", auth=True)
        if not response:
            raise InvalidResponseError(command=Commands.GET_STATUS, response=response[0])
        
        return response[0] == "ÿÿÿÿprint"
    
    def kick(self, player_id: int, reason: str = "You have been kicked") -> bool:
        response = self.send_command(Commands.KICK, arg=f"{player_id} {reason}", auth=True)
        if not response:
            raise InvalidResponseError(command=Commands.GET_STATUS, response=response[0])
        
        return response[0] == "ÿÿÿÿprint"