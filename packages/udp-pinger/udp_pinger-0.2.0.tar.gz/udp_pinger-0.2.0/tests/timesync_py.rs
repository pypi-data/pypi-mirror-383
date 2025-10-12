use pyo3::ffi::c_str;
use pyo3::prelude::*;
use pyo3::types::PyModule;
use std::ffi::CString;

const PY_FILE: &str = "tests/timesync.py";

fn main() {
    Python::attach(|py| {
        let code = std::fs::read_to_string(PY_FILE).unwrap();
        let code = CString::new(code).unwrap();
        let module =
            PyModule::from_code(py, &code, c_str!("timesync.py"), c_str!("timesync")).unwrap();
        udp_pinger::py::py_module(&module).unwrap();
        py.run(c_str!("main()"), None, Some(&module.dict()))
            .unwrap();
    })
}
