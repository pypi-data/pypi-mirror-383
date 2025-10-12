use std::{net::Ipv4Addr, time::Duration};

fn read_addr_from_arg() -> Ipv4Addr {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 2 {
        println!("Alternate usage: cargo run --example ping <IP_ADDRESS>");
    }
    args.get(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(Ipv4Addr::new(127, 0, 0, 1))
}

async fn async_main() {
    let addr = read_addr_from_arg();
    println!("Pinging {}", addr);
    let p = udp_pinger::AsyncPinger::try_new(addr).await.unwrap();
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

fn main() {
    smol::block_on(async_main());
}
