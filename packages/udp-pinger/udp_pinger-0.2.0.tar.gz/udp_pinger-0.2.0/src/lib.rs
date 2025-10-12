#[cfg(feature = "py")]
pub mod py;

use std::{
    fmt,
    net::{IpAddr, Ipv4Addr, SocketAddr, UdpSocket},
    sync::{
        Arc, Mutex, Weak,
        atomic::{AtomicBool, Ordering},
    },
    thread,
    time::{Duration, Instant, SystemTime},
};

#[cfg(feature = "async")]
use async_net::UdpSocket as AsyncUdpSocket;

use circular_buffer::CircularBuffer;
use event_listener::{Event, Listener};

pub(crate) static SNAPSHOT: std::sync::LazyLock<TimePair> = std::sync::LazyLock::new(TimePair::now);

/// Convert a SystemTime to an Instant, if possible.
/// This is only possible if the SystemTime is after the start of this program.
/// Otherwise, returns None.
pub fn system_to_instant(system_time: SystemTime) -> Option<Instant> {
    let delta = system_time
        .duration_since(SNAPSHOT.system)
        .unwrap_or(Duration::ZERO);
    Some(SNAPSHOT.instant + delta)
}

#[derive(Debug, Clone, Copy)]
struct TimePair {
    system: SystemTime,
    instant: Instant,
}
impl TimePair {
    fn now() -> Self {
        TimePair {
            system: SystemTime::now(),
            instant: Instant::now(),
        }
    }
}

#[derive(Debug, thiserror::Error)]
pub enum PingError {
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Poisoned lock")]
    PoisonedLock,
    #[error("Too few samples")]
    TooFewSamples,
    #[error("Timeout")]
    Timeout,
}

impl<T> From<std::sync::PoisonError<T>> for PingError {
    fn from(_: std::sync::PoisonError<T>) -> Self {
        PingError::PoisonedLock
    }
}

type PingResult<T> = Result<T, PingError>;

/// A single ping attempt result.
#[derive(Debug, Clone)]
pub enum PingSample {
    /// A successful ping attempt.
    Success {
        /// Wall-clock when the attempt was made.
        at: SystemTime,
        /// Round-trip time.
        latency: Duration,
    },
    Failure {
        /// Wall-clock when the attempt was made.
        at: SystemTime,
        /// Short error detail (e.g., "timeout", OS error).
        error: String,
    },
}

impl PingSample {
    pub fn success(start: Instant) -> Self {
        PingSample::Success {
            at: SystemTime::now(),
            latency: start.elapsed(),
        }
    }

    pub fn failure(error: impl Into<String>) -> Self {
        PingSample::Failure {
            at: SystemTime::now(),
            error: error.into(),
        }
    }

    pub fn at(&self) -> SystemTime {
        match self {
            PingSample::Success { at, .. } => *at,
            PingSample::Failure { at, .. } => *at,
        }
    }

    pub fn ok(&self) -> bool {
        matches!(self, PingSample::Success { .. })
    }

    pub fn latency(&self) -> Option<Duration> {
        match self {
            PingSample::Success { latency, .. } => Some(*latency),
            PingSample::Failure { .. } => None,
        }
    }

    pub fn error(&self) -> Option<&str> {
        match self {
            PingSample::Success { .. } => None,
            PingSample::Failure { error, .. } => Some(error),
        }
    }
}

impl std::fmt::Display for PingSample {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            PingSample::Success { at, latency } => {
                let at_secs = match at.duration_since(std::time::UNIX_EPOCH) {
                    Ok(dur) => format!("{}", dur.as_secs_f64()),
                    Err(_) => "unknown".into(),
                };
                write!(
                    f,
                    "PingSample(at={}, ok=true, latency={:.3} ms)",
                    at_secs,
                    latency.as_secs_f64() * 1000.0
                )
            }
            PingSample::Failure { at, error } => {
                let at_secs = match at.duration_since(std::time::UNIX_EPOCH) {
                    Ok(dur) => format!("{}", dur.as_secs_f64()),
                    Err(_) => "unknown".into(),
                };
                write!(
                    f,
                    "PingSample(at={}, ok=false, error=\"{}\")",
                    at_secs, error
                )
            }
        }
    }
}

/// Aggregate stats across the in-memory window.
#[derive(Clone, Debug, Default)]
pub struct PingStats {
    pub total: usize,
    pub up: usize,
    pub down: usize,
    /// Uptime over the window, in percent.
    pub uptime_percent: f64,
    /// Avg latency in ms over successful samples.
    pub avg_latency_ms: Option<f64>,
}

impl fmt::Display for PingStats {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if let Some(avg) = self.avg_latency_ms {
            write!(
                f,
                "PingStats {{ total={}, up={}, down={}, uptime={:.1}%, avg_latency={:.1} ms }}",
                self.total, self.up, self.down, self.uptime_percent, avg
            )
        } else {
            write!(
                f,
                "PingStats {{ total={}, up={}, down={}, uptime={:.1}%, avg_latency=— }}",
                self.total, self.up, self.down, self.uptime_percent
            )
        }
    }
}

pub enum EitherUdpSocket {
    Sync(UdpSocket),
    #[cfg(feature = "async")]
    Async(AsyncUdpSocket),
}

struct PingStorage {
    history: Mutex<CircularBuffer<64, PingSample>>,
    history_update_event: Event,
    history_update_flag: AtomicBool,
    socket: EitherUdpSocket,
}

impl PingStorage {
    fn try_new(sock: EitherUdpSocket, addr: IpAddr) -> PingResult<Self> {
        let dest = if cfg!(feature = "alternate_port") {
            SocketAddr::new(addr, 33434)
        } else {
            SocketAddr::new(addr, 59999)
        };
        match &sock {
            EitherUdpSocket::Sync(s) => s.connect(dest),
            #[cfg(feature = "async")]
            EitherUdpSocket::Async(s) => futures::executor::block_on(s.connect(dest)),
        }?;
        Ok(Self {
            history: Mutex::new(CircularBuffer::new()),
            history_update_event: Event::new(),
            history_update_flag: AtomicBool::new(false),
            socket: sock,
        })
    }

    fn add_sample(&self, sample: PingSample) -> PingResult<()> {
        let mut history = self.history.lock()?;
        history.push_back(sample);
        self.history_update_flag.store(true, Ordering::SeqCst);
        self.history_update_event.notify(u32::MAX);
        Ok(())
    }

    fn ema(&self, alpha: f64) -> PingResult<f64> {
        let history = self.history.lock()?;
        let rtts: Vec<f64> = history
            .iter()
            .filter_map(|s| s.latency().map(|d| d.as_secs_f64() * 1000.0))
            .collect();
        if rtts.is_empty() {
            return Err(PingError::TooFewSamples);
        }
        let mut ema = rtts[0];
        for &lat in &rtts[1..] {
            ema = alpha * lat + (1.0 - alpha) * ema;
        }
        Ok(ema * 0.495)
    }

    fn confidence_interval(&self) -> PingResult<(f64, f64)> {
        let history = self.history.lock()?;
        let rtts: Vec<f64> = history
            .iter()
            .filter_map(|s| s.latency().map(|d| d.as_secs_f64() * 1000.0))
            .collect();
        if rtts.len() < 2 {
            return Err(PingError::TooFewSamples);
        }

        let n = rtts.len() as f64;
        let mean = rtts.iter().copied().sum::<f64>() / n;
        let var = rtts.iter().map(|&x| (x - mean).powi(2)).sum::<f64>() / (n - 1.0);
        let stddev = var.sqrt();
        let moe = 1.96 * stddev / n.sqrt();
        Ok(((mean - moe) * 0.495, (mean + moe) * 0.495))
    }

    pub fn stats(&self) -> PingStats {
        let buf = self.history.lock().unwrap();
        let total = buf.len();
        let (mut up, mut down) = (0usize, 0usize);
        let mut sum_ms = 0.0f64;
        let mut n_latency = 0usize;

        for s in buf.iter() {
            match s {
                PingSample::Success { latency, .. } => {
                    up += 1;
                    sum_ms += latency.as_secs_f64() * 1000.0;
                    n_latency += 1;
                }
                PingSample::Failure { .. } => {
                    down += 1;
                }
            }
        }

        let uptime_percent = if total == 0 {
            0.0
        } else {
            (up as f64) * 100.0 / (total as f64)
        };

        let avg_latency_ms = if n_latency == 0 {
            None
        } else {
            Some(sum_ms / (n_latency as f64))
        };

        PingStats {
            total,
            up,
            down,
            uptime_percent,
            avg_latency_ms,
        }
    }

    pub fn is_reachable(&self, window: usize) -> PingResult<bool> {
        let buf = self.history.lock()?;
        if window == 0 {
            return Err(PingError::TooFewSamples);
        }
        if buf.len() < window {
            return Err(PingError::TooFewSamples);
        }
        Ok(buf.iter().rev().take(window).any(|s| s.ok()))
    }
}

fn worker_loop(
    timeout: Duration,
    interval: Duration,
    shared: Arc<PingStorage>,
    is_alive: Weak<AtomicBool>,
) {
    // Do an immediate first ping, then tick at a fixed cadence.
    let mut last_tick = Instant::now();
    let _ = do_one_ping(timeout, &shared);

    loop {
        let next_tick = last_tick + interval;
        let now = Instant::now();

        if now < next_tick {
            let wait = next_tick - now;
            thread::park_timeout(wait);
            if !is_alive
                .upgrade()
                .is_some_and(|a| a.load(Ordering::SeqCst))
            {
                break;
            }
        } else if now > next_tick + interval {
            // We are late; skip to next tick.
            last_tick = now;
            continue;
        }

        last_tick = Instant::now();
        let _ = do_one_ping(timeout, &shared);
    }
}

fn intake_ping(
    recv: std::io::Result<usize>,
    start: Instant,
    shared: &Arc<PingStorage>,
) -> PingResult<PingSample> {
    match recv {
        Ok(_n) => {
            shared.add_sample(PingSample::success(start))?;
        }
        Err(ref e) if e.kind() == std::io::ErrorKind::ConnectionRefused => {
            let elapsed = start.elapsed();
            shared.add_sample(PingSample::Success {
                at: SystemTime::now(),
                latency: elapsed,
            })?;
        }
        Err(ref e)
            if e.kind() == std::io::ErrorKind::WouldBlock
                || e.kind() == std::io::ErrorKind::TimedOut =>
        {
            shared.add_sample(PingSample::failure("timeout"))?;
        }
        Err(e) => {
            shared.add_sample(PingSample::failure(format!("udp recv error: {e}")))?;
        }
    }
    let buf = shared.history.lock()?;
    let back = buf.back().cloned();
    drop(buf);
    back.ok_or(PingError::TooFewSamples)
}

#[allow(irrefutable_let_patterns)]
fn do_one_ping(timeout: Duration, shared: &Arc<PingStorage>) -> PingResult<PingSample> {
    if let EitherUdpSocket::Sync(sock) = &shared.socket {
        sock.set_read_timeout(Some(timeout))?;

        let start = Instant::now();
        let payload = b"udp ping probe";

        if let Err(e) = sock.send(payload) {
            let sample = PingSample::failure(format!("udp send error: {e}"));
            shared.add_sample(sample.clone())?;
            return Ok(sample);
        }

        intake_ping(sock.recv(&mut [0u8; 128]), start, shared)
    } else {
        unreachable!("do_one_ping called on async socket");
    }
}

/// The main pinger struct.
///
/// This struct manages a background thread that periodically sends UDP packets to a specified address
/// and records the round-trip time (RTT) of each ping attempt. It maintains an in-memory history of ping samples
/// and provides methods to retrieve statistics and perform forced pings.
pub struct Pinger {
    shared: Arc<PingStorage>,
    is_alive: Arc<AtomicBool>,
    join: Option<thread::JoinHandle<()>>,
}

impl Pinger {
    /// Create a new Pinger instance for the given IP address.
    /// The pinger is not started until `start()` is called.
    ///
    /// # Errors
    /// IoError if the socket cannot be created or bound.
    pub fn try_new(addr: impl Into<IpAddr>) -> PingResult<Self> {
        let sock = EitherUdpSocket::Sync(UdpSocket::bind(SocketAddr::new(
            IpAddr::V4(Ipv4Addr::UNSPECIFIED),
            0,
        ))?);
        Ok(Self {
            shared: Arc::new(PingStorage::try_new(sock, addr.into())?),
            is_alive: Arc::new(AtomicBool::new(true)),
            join: None,
        })
    }

    /// Start the background thread that performs periodic pings.
    /// If the pinger is already started, this is a no-op.
    ///
    /// # Errors
    /// IoError if the background thread cannot be started.
    pub fn start_periodic(
        &mut self,
        interval: Duration,
        per_ping_timeout: Duration,
    ) -> PingResult<()> {
        if self.join.is_none() {
            let shared_clone = self.shared.clone();

            let weak_alive = Arc::downgrade(&self.is_alive);
            let handle = thread::Builder::new()
                .name("icmp-pinger".into())
                .spawn(move || worker_loop(per_ping_timeout, interval, shared_clone, weak_alive))?;

            self.join = Some(handle);
        }
        Ok(())
    }

    /// Stop the background pinging thread and wait for it to exit.
    /// If the pinger is not running, this is a no-op.
    /// After stopping, the pinger can be restarted by calling `start()` again.
    pub fn stop_periodic(&mut self) {
        self.is_alive.store(false, Ordering::SeqCst);
        if let Some(j) = self.join.take() {
            j.thread().unpark();
            let _ = j.join();
        }
    }

    /// Perform a single ping attempt immediately, blocking until it completes or times out.
    /// This information is also merged into the periodic pinging history.
    ///
    /// # Errors
    /// [PingError::PoisonedLock] if the internal lock is poisoned.
    #[inline]
    pub fn ping(&self, timeout: Duration) -> PingResult<PingSample> {
        do_one_ping(timeout, &self.shared)
    }

    /// Get the current estimated moving average latency.
    /// This uses an exponential moving average (EMA) with the given alpha.
    /// Alpha should be between 0.0 and 1.0, where higher values give more weight to recent samples.
    ///
    /// # Errors
    /// [PingError::TooFewSamples] if there are not enough samples to compute the EMA.
    pub fn latency_ema(&self, alpha: f64) -> PingResult<f64> {
        self.shared.ema(alpha)
    }

    /// Get the current 95% confidence interval for the latency.
    /// This is based on the sample mean and standard deviation.
    ///
    /// # Errors
    /// [PingError::TooFewSamples] if there are not enough samples to compute the confidence interval.
    pub fn latency_confidence_interval(&self) -> PingResult<(f64, f64)> {
        self.shared.confidence_interval()
    }

    /// Wait for a new ping sample to be available, up to the given timeout.
    /// If a new sample is available, return it. Otherwise, return None.
    ///
    /// # Errors
    /// [PingError::PoisonedLock] if the internal lock is poisoned.
    /// [PingError::Timeout] if no new sample is available within the timeout.
    pub fn wait_for_sample(&self, timeout: Duration) -> PingResult<PingSample> {
        if self.shared.history_update_flag.load(Ordering::SeqCst) {
            let buf = self.shared.history.lock()?;
            let back = buf.back().cloned();
            drop(buf);
            if back.is_some() {
                self.shared
                    .history_update_flag
                    .store(false, Ordering::SeqCst);
                return back.ok_or(PingError::TooFewSamples);
            }
        };
        let listener = self.shared.history_update_event.listen();
        let race = listener.wait_timeout(timeout);
        match race {
            Some(_) => {
                let buf = self.shared.history.lock()?;
                let back = buf.back().cloned();
                drop(buf);
                self.shared
                    .history_update_flag
                    .store(false, Ordering::SeqCst);
                back.ok_or(PingError::TooFewSamples)
            }
            None => Err(PingError::Timeout),
        }
    }

    /// Check if the target is reachable based on the last `window` samples.
    /// Returns true if any of the last `window` samples were successful.
    ///
    /// # Errors
    /// [PingError::TooFewSamples] if there are not enough samples to determine reachability.
    pub fn is_reachable(&self, window: usize) -> PingResult<bool> {
        self.shared.is_reachable(window)
    }

    /// Get aggregate statistics over the in-memory sample window.
    /// This includes total samples, number of successful and failed pings,
    /// uptime percentage, and average latency.
    pub fn stats(&self) -> PingStats {
        self.shared.stats()
    }
}

#[cfg(feature = "async")]
async fn do_one_ping_async(timeout: Duration, shared: &Arc<PingStorage>) -> PingResult<PingSample> {
    if let EitherUdpSocket::Async(sock) = &shared.socket {
        let start = Instant::now();
        let payload = b"udp ping probe";

        if let Err(e) = sock.send(payload).await {
            let sample = PingSample::failure(format!("udp send error: {e}"));
            shared.add_sample(sample.clone())?;
            return Ok(sample);
        }

        let mut buf = [0u8; 128];
        let recv_fut = sock.recv(&mut buf);
        let recv_result = futures::future::select(
            Box::pin(recv_fut),
            Box::pin(async_io::Timer::after(timeout)),
        )
        .await;

        match recv_result {
            futures::future::Either::Left((recv, _)) => intake_ping(recv, start, shared),
            futures::future::Either::Right((_, _)) => {
                shared.add_sample(PingSample::failure("timeout"))?;
                Err(PingError::Timeout)
            }
        }
    } else {
        unreachable!("do_one_ping_async called on sync socket");
    }
}

/// The main pinger struct.
///
/// This struct manages a background thread that periodically sends UDP packets to a specified address
/// and records the round-trip time (RTT) of each ping attempt. It maintains an in-memory history of ping samples
/// and provides methods to retrieve statistics and perform forced pings.
#[cfg(feature = "async")]
#[derive(Clone)]
pub struct AsyncPinger {
    shared: Arc<PingStorage>,
}

#[cfg(feature = "async")]
impl AsyncPinger {
    /// Create a new Pinger instance for the given IP address.
    /// The pinger is not started until `start()` is called.
    ///
    /// # Errors
    /// IoError if the socket cannot be created or bound.
    pub async fn try_new(addr: impl Into<IpAddr>) -> PingResult<Self> {
        let sock = EitherUdpSocket::Async(
            AsyncUdpSocket::bind(SocketAddr::new(IpAddr::V4(Ipv4Addr::UNSPECIFIED), 0)).await?,
        );
        Ok(Self {
            shared: Arc::new(PingStorage::try_new(sock, addr.into())?),
        })
    }

    /// Creates an asynchronous future that performs periodic pings.
    /// The future runs until dropped or cancelled.
    /// This can be used instead of [`Pinger::start_periodic()`] to integrate with an async runtime.
    pub fn periodic(
        &self,
        interval: Duration,
        per_ping_timeout: Duration,
    ) -> impl std::future::Future<Output = ()> + '_ {
        let shared_clone = self.shared.clone();
        async move {
            let mut last_tick = Instant::now();
            // Do an immediate first ping, then tick at a fixed cadence.
            let _ = do_one_ping_async(per_ping_timeout, &shared_clone).await;

            loop {
                let next_tick = last_tick + interval;
                let now = Instant::now();

                if now < next_tick {
                    let wait = next_tick - now;
                    async_io::Timer::after(wait).await;
                } else if now > next_tick + interval {
                    // We are late; skip to next tick.
                    last_tick = now;
                    continue;
                }

                last_tick = Instant::now();
                let _ = do_one_ping_async(per_ping_timeout, &shared_clone).await;
            }
        }
    }

    /// Perform a single ping attempt immediately, asynchronously, until it completes or times out.
    /// This information is also merged into the periodic pinging history.
    ///
    /// # Errors
    /// [PingError::PoisonedLock] if the internal lock is poisoned.
    #[cfg(feature = "async")]
    #[inline]
    pub async fn ping(&self, timeout: Duration) -> PingResult<PingSample> {
        do_one_ping_async(timeout, &self.shared).await
    }

    /// Wait for a new ping sample to be available, up to the given timeout.
    /// If a new sample is available, return it. Otherwise, return None.
    ///
    /// # Errors
    /// [PingError::PoisonedLock] if the internal lock is poisoned.
    /// [PingError::Timeout] if no new sample is available within the timeout.
    pub async fn wait_for_sample(&self, timeout: Duration) -> PingResult<PingSample> {
        if self.shared.history_update_flag.load(Ordering::SeqCst) {
            let buf = self.shared.history.lock()?;
            let back = buf.back().cloned();
            drop(buf);
            if back.is_some() {
                self.shared
                    .history_update_flag
                    .store(false, Ordering::SeqCst);
                return back.ok_or(PingError::TooFewSamples);
            }
        };
        let listener = self.shared.history_update_event.listen();
        let race =
            futures::future::select(listener, Box::pin(async_io::Timer::after(timeout))).await;
        match race {
            futures::future::Either::Left((_, _)) => {
                let buf = self.shared.history.lock()?;
                let back = buf.back().cloned();
                drop(buf);
                self.shared
                    .history_update_flag
                    .store(false, Ordering::SeqCst);
                back.ok_or(PingError::TooFewSamples)
            }
            futures::future::Either::Right((_, _)) => Err(PingError::Timeout),
        }
    }

    /// Get the current estimated moving average latency.
    /// This uses an exponential moving average (EMA) with the given alpha.
    /// Alpha should be between 0.0 and 1.0, where higher values give more weight to recent samples.
    ///
    /// # Errors
    /// [PingError::TooFewSamples] if there are not enough samples to compute the EMA.
    pub fn latency_ema(&self, alpha: f64) -> PingResult<f64> {
        self.shared.ema(alpha)
    }

    /// Get the current 95% confidence interval for the latency.
    /// This is based on the sample mean and standard deviation.
    ///
    /// # Errors
    /// [PingError::TooFewSamples] if there are not enough samples to compute the confidence interval.
    pub fn latency_confidence_interval(&self) -> PingResult<(f64, f64)> {
        self.shared.confidence_interval()
    }

    /// Check if the target is reachable based on the last `window` samples.
    /// Returns true if any of the last `window` samples were successful.
    ///
    /// # Errors
    /// [PingError::TooFewSamples] if there are not enough samples to determine reachability.
    pub fn is_reachable(&self, window: usize) -> PingResult<bool> {
        self.shared.is_reachable(window)
    }

    /// Get aggregate statistics over the in-memory sample window.
    /// This includes total samples, number of successful and failed pings,
    /// uptime percentage, and average latency.
    pub fn stats(&self) -> PingStats {
        self.shared.stats()
    }
}

/// Keeps track of time synchronization between local system clock and remote clock.
/// The remote clock is assumed to be monotonically increasing at the same rate as the local clock.
/// The remote clock can be in any time domain (e.g., epoch time, time since boot, etc.).
#[derive(Debug, Clone, Copy)]
pub struct TimeSync {
    genesis: TimePair,
    genesis_age: Duration,
    latency: Duration,
}

impl TimeSync {
    /// Create a new TimeSync with the given remote time at the current instant.
    pub fn new(remote_time: impl Into<Duration>) -> Self {
        TimeSync {
            genesis: TimePair::now(),
            genesis_age: remote_time.into(),
            latency: Duration::from_secs(0),
        }
    }

    /// Create a new TimeSync with the given remote time and latency at the current instant.
    pub fn new_with_latency(
        remote_time: impl Into<Duration>,
        latency: impl Into<Duration>,
    ) -> Self {
        let latency = latency.into();
        TimeSync {
            genesis: TimePair::now(),
            genesis_age: remote_time.into() + latency,
            latency,
        }
    }

    /// Adjust the remote time by adding an offset.
    /// This is distinctly different from latency adjustment.
    /// Use this to correct for clock drift or discontinuities.
    pub fn add_offset(&mut self, offset: Duration) {
        self.genesis_age += offset;
    }

    /// Adjust the remote time by subtracting an offset.
    /// This is distinctly different from latency adjustment.
    /// Use this to correct for clock drift or discontinuities.
    pub fn sub_offset(&mut self, offset: Duration) {
        self.genesis_age = self.genesis_age.saturating_sub(offset);
    }

    /// Set the latency to the given value.
    /// This will adjust the remote time accordingly
    /// and override any previous latency setting but not offsets.
    pub fn set_latency(&mut self, latency: Duration) {
        let old_latency = self.latency;
        self.genesis_age = self.genesis_age + latency - old_latency;
        self.latency = latency;
    }

    /// Get the system time corresponding to the given remote time.
    pub fn system_time_during_remote(&self, remote_time: impl Into<Duration>) -> SystemTime {
        let remote_duration = remote_time.into();
        let remote_elapsed = remote_duration - self.genesis_age;
        self.genesis.system + remote_elapsed
    }

    /// Get the remote time corresponding to the given system time.
    pub fn remote_time_during_system(&self, system_time: SystemTime) -> Duration {
        system_time
            .duration_since(self.genesis.system)
            .unwrap_or_else(|_| Duration::from_secs(0))
            + self.genesis_age
    }

    /// Get the instant corresponding to the given remote time.
    pub fn instant_during_remote(&self, remote_time: impl Into<Duration>) -> Instant {
        let remote_duration = remote_time.into();
        let remote_elapsed = remote_duration - self.genesis_age;
        self.genesis.instant + remote_elapsed
    }

    /// Get the remote time corresponding to the given instant.
    pub fn remote_time_during_instant(&self, instant: Instant) -> Duration {
        instant.duration_since(self.genesis.instant) + self.genesis_age
    }
}
