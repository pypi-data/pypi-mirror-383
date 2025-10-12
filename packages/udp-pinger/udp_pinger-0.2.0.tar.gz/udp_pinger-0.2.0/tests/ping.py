# The rust example effectively runs `from udp_pinger import *`
# loads this file as a module and then runs the main function.
from typing import TYPE_CHECKING
import sys

if TYPE_CHECKING:
    from udp_pinger import Pinger


def read_addr_from_arg() -> str:
    if len(sys.argv) != 2:
        print("Alternate usage: python3 examples/ping.py <IP_ADDRESS>")
    return sys.argv[1] if len(sys.argv) == 2 else "127.0.0.1"


def main() -> None:
    addr = read_addr_from_arg()
    print(f"Pinging {addr}")
    p = Pinger(addr)  # type: ignore
    p.ping(timeout_secs=1.0)
    p.start_periodic(interval_secs=0.5, per_ping_timeout_secs=0.35)
    for _ in range(4):
        sample = p.wait_for_sample(timeout_secs=2.0)
        if sample is not None:
            print(f"Sample: {sample}")
        else:
            raise RuntimeError("No sample received in 2 second, exiting.")
    p.stop_periodic()
    assert p.is_reachable(2) is True
    print(f"Latency: {p.latency_ms()} ms")
    print(p.stats())
