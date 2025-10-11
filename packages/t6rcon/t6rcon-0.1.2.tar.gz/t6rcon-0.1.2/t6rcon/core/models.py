from dataclasses import dataclass
from typing import Optional, Union
from pydantic import BaseModel

class ServerStatus(BaseModel):
    com_maxclients: int
    fs_game: Optional[str] = None
    g_gametype: str
    g_randomSeed: str
    gamename: str
    mapname: str
    playlist_enabled: int
    playlist_entry: int
    protocol: int
    scr_team_fftype: int
    shortversion: int
    sv_allowAimAssist: int
    sv_allowAnonymous: int
    sv_clientFpsLimit: int
    sv_disableClientConsole: int
    sv_hostname: str
    sv_maxclients: int
    sv_maxPing: int
    sv_minPing: int
    sv_privateClients: int
    sv_privateClientsForClients: int
    sv_pure: int
    sv_voice: int
    sv_wwwBaseURL: Optional[str] = None
    password: bool
    mod: bool

    class Config: extra = "ignore"

class ServerInfo(BaseModel):
    netfieldcheck: str
    protocol: int
    sessionmode: int
    hostname: str
    mapname: str
    isInGame: bool
    com_maxclients: int
    gametype: str
    game: Optional[str] = None
    ff: Optional[int] = None
    hw: int
    mod: int
    voice: int
    seckey: str
    secid: str
    hostaddr: str
    clients: Optional[int] = None

    class Config: extra = "ignore"

@dataclass
class Player:
    id: int
    player: str
    guid: Optional[str] = None

    ping: Optional[Union[str, int]] = None
    score: Optional[int] = None

    ip: Optional[str] = None
    port: Optional[int] = None
    qport: Optional[int] = None
    
    lastmsg: Optional[int] = None
    rating: Optional[int] = None