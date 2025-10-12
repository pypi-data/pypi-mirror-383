# The rust example effectively runs `from udp_pinger import *`
# loads this file as a module and then runs the main function.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from udp_pinger import TimeSync, now_ms


# use udp_pinger::{self, TimeSync};

# fn main() {
#     let ts = TimeSync::new(Duration::from_secs(5));
#     let should_be_5_past_no2 = ts.system_time_during_remote(Duration::from_secs(10));
#     assert!(should_be_5_past_no2 > std::time::SystemTime::now() + Duration::from_secs(4));
#     assert!(should_be_5_past_no2 < std::time::SystemTime::now() + Duration::from_secs(6));

#     let mut ts = TimeSync::new(Duration::from_secs(0));
#     ts.add_offset(Duration::from_secs(5));
#     let should_be_5_past = ts.system_time_during_remote(Duration::from_secs(10));
#     assert!(should_be_5_past > std::time::SystemTime::now() + Duration::from_secs(4));
#     assert!(should_be_5_past < std::time::SystemTime::now() + Duration::from_secs(6));

#     let mut ts = TimeSync::new(Duration::from_secs(10));
#     ts.sub_offset(Duration::from_secs(5));
#     let should_be_5_past_no = ts.system_time_during_remote(Duration::from_secs(10));
#     assert!(should_be_5_past_no > std::time::SystemTime::now() + Duration::from_secs(4));
#     assert!(should_be_5_past_no < std::time::SystemTime::now() + Duration::from_secs(6));

#     let ts = TimeSync::new(Duration::from_secs(10));
#     let now = std::time::SystemTime::now();
#     let should_be_10 = ts.remote_time_during_system(now);
#     assert!(should_be_10 > Duration::from_secs(9));
#     assert!(should_be_10 < Duration::from_secs(11));

#     let mut ts = TimeSync::new_with_latency(Duration::from_secs(15), Duration::from_secs(12));
#     ts.set_latency(Duration::from_secs(25));
#     let now = std::time::Instant::now();
#     let should_be_40 = ts.remote_time_during_instant(now);
#     assert!(should_be_40 > Duration::from_secs(39));
#     assert!(should_be_40 < Duration::from_secs(41));

#     let ts = TimeSync::new(Duration::from_secs(25));
#     let now = std::time::Instant::now();
#     let should_be_15 = ts.instant_during_remote(Duration::from_secs(40)) - now;
#     assert!(should_be_15 > Duration::from_secs(14));
#     assert!(should_be_15 < Duration::from_secs(16));

#     udp_pinger::system_to_instant(std::time::SystemTime::now()).unwrap();
#     std::thread::sleep(Duration::from_secs(2));

#     let now_system = std::time::SystemTime::now();
#     let now_instant = udp_pinger::system_to_instant(now_system).unwrap();
#     let delta = now_instant.duration_since(std::time::Instant::now());
#     assert!(delta < Duration::from_secs(1));
# }


def main() -> None:
    ts = TimeSync(5000)
    should_be_5_past_no2 = ts.system_time_during_remote(10000)
    assert 4000 < (should_be_5_past_no2 - now_ms()) < 6000

    ts = TimeSync(0)
    ts.add_offset(5000)
    should_be_5_past = ts.system_time_during_remote(10000)
    assert 4000 < (should_be_5_past - now_ms()) < 6000

    ts = TimeSync(10000)
    ts.sub_offset(5000)
    should_be_5_past_no = ts.system_time_during_remote(10000)
    assert 4000 < (should_be_5_past_no - now_ms()) < 6000

    ts = TimeSync(10000)
    now = now_ms()
    should_be_10 = ts.remote_time_during_system(now)
    assert 9000 < should_be_10 < 11000

    ts = TimeSync(15000, 25000)
    now = now_ms()
    should_be_40 = ts.remote_time_during_system(now)
    assert 39000 < should_be_40 < 41000

    ts = TimeSync(15000, 12000)
    ts.set_latency(25000)
    now = now_ms()
    should_be_40 = ts.remote_time_during_system(now)
    assert 39000 < should_be_40 < 41000
