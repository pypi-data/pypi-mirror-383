## A RCON module for Plutonium T6

### Installation:
```cmd
pip install t6rcon
```

### Simple Usage:
```python
from t6rcon import PlutoRcon

rcon = PlutoRCON(
    ip_addr  = "127.0.0.1",
    port     = 4976,
    password = "password",
)

rcon.kick(0, "You got kicked!")
rcon.tell(5, "Hello")

print(rcon.get_players())
```