# UDP Pinger

An implementation of a UDP-based ping utility.
This library does not require root privileges, unlike ICMP-based ping utilities.

## Usage

### Rust Example
```rust
use std::{net::Ipv4Addr, time::Duration};

use udp_pinger;

fn main() {
    let mut p = udp_pinger::Pinger::try_new(Ipv4Addr::new(10, 23, 16, 11)).unwrap();
    p.ping(Duration::from_secs(1)).unwrap();
    p.start_periodic(Duration::from_millis(500), Duration::from_millis(350))
        .unwrap();
    for _ in 0..4 {
        let opt_sample = p.wait_for_sample(Duration::from_secs(2));
        if let Ok(sample) = opt_sample {
            println!("Sample: {}", sample);
        } else {
            panic!("No sample received in 2 second, exiting.");
        }
    }
    p.stop_periodic();
    assert!(p.is_reachable(2).unwrap());
    println!("Latency: {:?}", p.latency_ema(0.1).unwrap());
    println!("{}", p.stats());
}
```
### Rust Async Example
```rust
use std::{net::Ipv4Addr, time::Duration};

use udp_pinger;

async fn main() {
    // works on any runtime, use smol here for simplicity
    let p = udp_pinger::AsyncPinger::try_new(Ipv4Addr::new(10, 23, 16, 11)).await.unwrap();
    p.ping(Duration::from_secs(1)).await.unwrap();
    {
        let ex = smol::Executor::new();
        ex.spawn(p.periodic(Duration::from_millis(500), Duration::from_millis(350)))
            .detach();
        let poller = async {
            for _ in 0..4 {
                let opt_sample = p.wait_for_sample(Duration::from_secs(2)).await;
                if let Ok(sample) = opt_sample {
                    println!("Sample: {}", sample);
                } else {
                    panic!("No sample received in 2 second, exiting.");
                }
            }
        };
        ex.run(poller).await;
    }
    assert!(p.is_reachable(2).unwrap());
    println!("Latency: {:?}", p.latency_ema(0.1).unwrap());
    println!("{}", p.stats());
}
```
### Python Bindings
```python
from udp_pinger import Pinger

def main() -> None:
    p = Pinger("10.23.15.11")
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
```

## Features
- `py`: Enables Python bindings using PyO3.
- `async`: Enables asynchronous support using generic async primitives.
- `alternate_port`: Uses an alternate UDP port (33434) for sending packets instead of the default (59999).

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.