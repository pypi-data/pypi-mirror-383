use std::{
    net::IpAddr,
    time::{Duration, SystemTime},
};

use pyo3::prelude::*;

use crate::{PingError, Pinger, TimeSync};

impl From<PingError> for pyo3::PyErr {
    fn from(e: PingError) -> Self {
        match e {
            PingError::Io(e) => pyo3::exceptions::PyIOError::new_err(format!("{}", e)),
            other => pyo3::exceptions::PyRuntimeError::new_err(format!("{}", other)),
        }
    }
}

#[pyo3::pyclass(name = "PingSample", frozen, str)]
pub struct PyPingSample {
    #[pyo3(get)]
    pub at: String,
    #[pyo3(get)]
    pub ok: bool,
    #[pyo3(get)]
    pub latency_ms: Option<f64>,
    #[pyo3(get)]
    pub error: Option<String>,
}

impl From<super::PingSample> for PyPingSample {
    fn from(s: super::PingSample) -> Self {
        let at = match s.at().duration_since(std::time::UNIX_EPOCH) {
            Ok(dur) => format!("{}", dur.as_secs_f64()),
            Err(_) => "unknown".into(),
        };
        let latency_ms = s.latency().map(|d| d.as_secs_f64() * 1000.0);
        Self {
            at,
            ok: s.ok(),
            latency_ms,
            error: s.error().map(ToString::to_string),
        }
    }
}

impl std::fmt::Display for PyPingSample {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        if self.ok {
            if let Some(latency) = self.latency_ms {
                write!(
                    f,
                    "PingSample(at={}, ok=true, latency={:.3} ms)",
                    self.at, latency
                )
            } else {
                write!(f, "PingSample(at={}, ok=true, latency=unknown)", self.at)
            }
        } else if let Some(err) = &self.error {
            write!(f, "PingSample(at={}, ok=false, error={})", self.at, err)
        } else {
            write!(f, "PingSample(at={}, ok=false, error=unknown)", self.at)
        }
    }
}

#[pyo3::pyclass(name = "PingStats", frozen, str)]
pub struct PyPingStats {
    #[pyo3(get)]
    pub total: usize,
    #[pyo3(get)]
    pub up: usize,
    #[pyo3(get)]
    pub down: usize,
    #[pyo3(get)]
    pub uptime_percent: f64,
    #[pyo3(get)]
    pub avg_latency_ms: Option<f64>,
}
impl From<super::PingStats> for PyPingStats {
    fn from(s: super::PingStats) -> Self {
        Self {
            total: s.total,
            up: s.up,
            down: s.down,
            uptime_percent: s.uptime_percent,
            avg_latency_ms: s.avg_latency_ms,
        }
    }
}

impl std::fmt::Display for PyPingStats {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        if let Some(avg_latency) = self.avg_latency_ms {
            write!(
                f,
                "PingStats(total={}, up={}, down={}, uptime_percent={:.2}%, avg_latency={:.3} ms)",
                self.total, self.up, self.down, self.uptime_percent, avg_latency
            )
        } else {
            write!(
                f,
                "PingStats(total={}, up={}, down={}, uptime_percent={:.2}%, avg_latency=unknown)",
                self.total, self.up, self.down, self.uptime_percent
            )
        }
    }
}

#[pyo3::pyclass(name = "Pinger")]
pub struct PyPinger {
    inner: Pinger,
}

#[pyo3::pymethods]
impl PyPinger {
    #[new]
    #[pyo3(signature = (addr))]
    pub fn new(addr: Bound<PyAny>) -> PyResult<Self> {
        let addr = addr.extract::<IpAddr>()?;
        let p = Pinger::try_new(addr)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("{}", e)))?;
        Ok(Self { inner: p })
    }

    #[pyo3(signature = (interval_secs, per_ping_timeout_secs))]
    pub fn start_periodic(
        &mut self,
        interval_secs: f64,
        per_ping_timeout_secs: f64,
    ) -> PyResult<()> {
        let interval = std::time::Duration::from_secs_f64(interval_secs);
        let timeout = std::time::Duration::from_secs_f64(per_ping_timeout_secs);
        self.inner
            .start_periodic(interval, timeout)
            .map_err(Into::into)
    }

    #[pyo3(signature = (timeout_secs=5.0))]
    pub fn wait_for_sample(&self, timeout_secs: f64) -> Option<PyPingSample> {
        let timeout = std::time::Duration::from_secs_f64(timeout_secs);
        self.inner.wait_for_sample(timeout).ok().map(Into::into)
    }

    #[pyo3(signature = (timeout_secs=1.0))]
    pub fn ping(&self, timeout_secs: f64) -> PyResult<PyPingSample> {
        let timeout = std::time::Duration::from_secs_f64(timeout_secs);
        self.inner
            .ping(timeout)
            .map_err(|e| {
                pyo3::exceptions::PyRuntimeError::new_err(format!("failed to send ping: {}", e))
            })
            .map(Into::into)
    }

    #[pyo3(signature = (window = 2))]
    pub fn is_reachable(&self, window: usize) -> bool {
        self.inner.is_reachable(window).unwrap_or(false)
    }

    #[pyo3(signature = ())]
    pub fn latency_ms(&self) -> Option<f64> {
        self.inner.latency_ema(0.1).ok()
    }

    #[pyo3(signature = ())]
    pub fn stats(&self) -> PyPingStats {
        self.inner.stats().into()
    }

    #[pyo3(signature = ())]
    pub fn stop_periodic(&mut self) {
        self.inner.stop_periodic();
    }
}

#[pyo3::pyclass(name = "TimeSync")]
pub struct PyTimeSync {
    inner: TimeSync,
}

impl From<TimeSync> for PyTimeSync {
    fn from(ts: TimeSync) -> Self {
        Self { inner: ts }
    }
}

#[pyo3::pymethods]
impl PyTimeSync {
    #[new]
    #[pyo3(signature = (remote_time_ms, latency_ms=0.0))]
    pub fn new(remote_time_ms: f64, latency_ms: f64) -> Self {
        let remote_time = Duration::from_secs_f64(remote_time_ms / 1000.0);
        let latency = Duration::from_secs_f64(latency_ms / 1000.0);
        let inner = if latency_ms == 0.0 {
            TimeSync::new(remote_time)
        } else {
            TimeSync::new_with_latency(remote_time, latency)
        };
        Self { inner }
    }

    #[pyo3(signature = (offset_ms))]
    pub fn add_offset(&mut self, offset_ms: f64) {
        let offset = std::time::Duration::from_secs_f64(offset_ms / 1000.0);
        self.inner.add_offset(offset);
    }

    #[pyo3(signature = (offset_ms))]
    pub fn sub_offset(&mut self, offset_ms: f64) {
        let offset = std::time::Duration::from_secs_f64(offset_ms / 1000.0);
        self.inner.sub_offset(offset);
    }

    #[pyo3(signature = (latency_ms))]
    pub fn set_latency(&mut self, latency_ms: f64) {
        let latency = std::time::Duration::from_secs_f64(latency_ms / 1000.0);
        self.inner.set_latency(latency);
    }

    #[pyo3(signature = (remote_time_ms))]
    pub fn system_time_during_remote(&self, remote_time_ms: f64) -> f64 {
        let remote_time = Duration::from_secs_f64(remote_time_ms / 1000.0);
        let system_time = self.inner.system_time_during_remote(remote_time);
        match system_time.duration_since(std::time::UNIX_EPOCH) {
            Ok(dur) => dur.as_secs_f64() * 1000.0,
            Err(_) => -1.0,
        }
    }

    #[pyo3(signature = (system_time_ms))]
    pub fn remote_time_during_system(&self, system_time_ms: f64) -> f64 {
        let system_time =
            std::time::UNIX_EPOCH + std::time::Duration::from_secs_f64(system_time_ms / 1000.0);
        let remote_time = self.inner.remote_time_during_system(system_time);
        remote_time.as_secs_f64() * 1000.0
    }
}

#[pyo3::pyfunction]
pub fn now_ms() -> f64 {
    match SystemTime::now().duration_since(std::time::UNIX_EPOCH) {
        Ok(dur) => dur.as_secs_f64() * 1000.0,
        Err(_) => -1.0,
    }
}

#[pyo3::pymodule(name = "_udp_pinger_core")]
pub fn py_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPingSample>()?;
    m.add_class::<PyPingStats>()?;
    m.add_class::<PyPinger>()?;
    m.add_class::<PyTimeSync>()?;
    m.add_function(pyo3::wrap_pyfunction!(now_ms, m)?)?;
    Ok(())
}
