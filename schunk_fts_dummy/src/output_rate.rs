use std::sync::{Arc, Mutex};
use std::time::Duration;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct OutputRateMode {
    pub enum_value: u8,
    pub requested_hz: u32,
    pub udp_packet_rate_hz: u32,
    pub samples_per_packet: usize,
    pub sample_period: Duration,
}

impl OutputRateMode {
    pub fn from_enum(value: u8) -> Option<Self> {
        match value {
            0 => Some(Self::new(0, 1000, 1000, 1)),
            1 => Some(Self::new(1, 500, 500, 1)),
            2 => Some(Self::new(2, 250, 250, 1)),
            3 => Some(Self::new(3, 100, 100, 1)),
            10 => Some(Self::new(10, 8000, 500, 16)),
            _ => None,
        }
    }

    pub fn packet_interval(self) -> Duration {
        Duration::from_secs_f64(1.0 / self.udp_packet_rate_hz as f64)
    }

    fn new(
        enum_value: u8,
        requested_hz: u32,
        udp_packet_rate_hz: u32,
        samples_per_packet: usize,
    ) -> Self {
        Self {
            enum_value,
            requested_hz,
            udp_packet_rate_hz,
            samples_per_packet,
            sample_period: Duration::from_secs_f64(1.0 / requested_hz as f64),
        }
    }
}

impl Default for OutputRateMode {
    fn default() -> Self {
        Self::from_enum(0).unwrap()
    }
}

#[derive(Clone, Debug)]
pub struct OutputRateState {
    mode: Arc<Mutex<OutputRateMode>>,
}

impl OutputRateState {
    pub fn new() -> Self {
        Self {
            mode: Arc::new(Mutex::new(OutputRateMode::default())),
        }
    }

    pub fn get(&self) -> OutputRateMode {
        *self.mode.lock().unwrap()
    }

    pub fn set_enum(&self, value: u8) -> bool {
        let Some(mode) = OutputRateMode::from_enum(value) else {
            return false;
        };
        *self.mode.lock().unwrap() = mode;
        true
    }
}

impl Default for OutputRateState {
    fn default() -> Self {
        Self::new()
    }
}
