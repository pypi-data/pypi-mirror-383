use crate::request::{Request, RequestBody};
use crate::response::{Response, SyncResponse};
use pyo3::coroutine::CancelHandle;
use pyo3::prelude::*;
use pyo3::types::PyType;

#[pyclass(extends=Request)]
pub struct ConsumedRequest;

#[pyclass(extends=Request)]
pub struct SyncConsumedRequest;

#[pymethods]
impl ConsumedRequest {
    pub async fn send(slf: Py<Self>, #[pyo3(cancel_handle)] cancel: CancelHandle) -> PyResult<Py<Response>> {
        let resp = Request::send_inner(slf.as_any(), cancel).await?;
        Python::attach(|py| Response::new_py(py, resp))
    }

    fn __copy__(slf: PyRef<Self>, py: Python) -> PyResult<Py<Self>> {
        Self::new_py(py, slf.as_super().try_clone_inner(py, None)?)
    }

    #[classmethod]
    pub fn from_request_and_body(
        _cls: &Bound<'_, PyType>,
        py: Python,
        request: Bound<Self>,
        body: Option<Py<RequestBody>>,
    ) -> PyResult<Py<Self>> {
        Self::new_py(py, request.try_borrow()?.as_super().try_clone_inner(py, body)?)
    }
}
impl ConsumedRequest {
    pub fn new_py(py: Python, inner: Request) -> PyResult<Py<Self>> {
        Py::new(py, PyClassInitializer::from(inner).add_subclass(Self))
    }
}

#[pymethods]
impl SyncConsumedRequest {
    pub fn send(slf: Bound<Self>, py: Python) -> PyResult<Py<SyncResponse>> {
        let resp = Request::blocking_send_inner(slf.as_super())?;
        SyncResponse::new_py(py, resp)
    }

    fn __copy__(slf: PyRef<Self>, py: Python) -> PyResult<Py<Self>> {
        Self::new_py(py, slf.as_super().try_clone_inner(py, None)?)
    }

    #[classmethod]
    pub fn from_request_and_body(
        _cls: &Bound<'_, PyType>,
        py: Python,
        request: Bound<Self>,
        body: Option<Py<RequestBody>>,
    ) -> PyResult<Py<Self>> {
        Self::new_py(py, request.try_borrow()?.as_super().try_clone_inner(py, body)?)
    }
}
impl SyncConsumedRequest {
    pub fn new_py(py: Python, inner: Request) -> PyResult<Py<Self>> {
        Py::new(py, PyClassInitializer::from(inner).add_subclass(Self))
    }
}
