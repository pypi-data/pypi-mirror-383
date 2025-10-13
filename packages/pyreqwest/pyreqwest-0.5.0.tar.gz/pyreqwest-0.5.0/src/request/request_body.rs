use crate::asyncio::OnceTaskLocal;
use crate::internal::body_stream::BodyStream;
use bytes::Bytes;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::sync::MutexExt;
use pyo3::{PyTraverseError, PyVisit};
use pyo3_bytes::PyBytes;
use std::sync::{Mutex, MutexGuard};

#[pyclass(frozen)]
pub struct RequestBody(Mutex<Option<InnerBody>>);

#[pymethods]
impl RequestBody {
    #[staticmethod]
    pub fn from_text(body: String) -> Self {
        Self::new(InnerBody::Bytes(body.into()))
    }

    #[staticmethod]
    pub fn from_bytes(body: PyBytes) -> Self {
        Self::new(InnerBody::Bytes(body.into_inner()))
    }

    #[staticmethod]
    pub fn from_stream(stream: Bound<PyAny>) -> PyResult<Self> {
        Ok(Self::new(InnerBody::Stream(BodyStream::new(stream)?)))
    }

    fn copy_bytes(&self, py: Python) -> PyResult<Option<PyBytes>> {
        match self.lock(py)?.as_ref() {
            Some(InnerBody::Bytes(bytes)) => Ok(Some(py.detach(|| PyBytes::from(bytes.clone())))),
            Some(InnerBody::Stream(_)) => Ok(None),
            None => Err(PyRuntimeError::new_err("Request body already consumed")),
        }
    }

    fn get_stream(&self, py: Python) -> PyResult<Option<Py<PyAny>>> {
        match self.lock(py)?.as_ref() {
            Some(InnerBody::Bytes(_)) => Ok(None),
            Some(InnerBody::Stream(stream)) => Ok(Some(stream.get_stream()?.clone_ref(py))),
            None => Err(PyRuntimeError::new_err("Request body already consumed")),
        }
    }

    fn __copy__(&self, py: Python) -> PyResult<Self> {
        self.try_clone(py)
    }

    pub fn __repr__(&self, py: Python) -> PyResult<String> {
        let type_name = py.get_type::<Self>().name()?;
        match self.lock(py)?.as_ref() {
            Some(InnerBody::Bytes(bytes)) => Ok(format!("{}(len={})", type_name, bytes.len())),
            Some(InnerBody::Stream(stream)) => {
                let stream_repr = stream.get_stream()?.bind(py).repr()?;
                Ok(format!("{}(stream={})", type_name, stream_repr.to_str()?))
            }
            None => Ok(format!("{}(<already consumed>)", type_name)),
        }
    }

    // :NOCOV_START
    pub fn __traverse__(&self, visit: PyVisit<'_>) -> Result<(), PyTraverseError> {
        let Ok(inner) = self.0.try_lock() else {
            return Ok(());
        };
        match inner.as_ref() {
            Some(InnerBody::Bytes(_)) => Ok(()),
            Some(InnerBody::Stream(stream)) => stream.__traverse__(visit),
            None => Ok(()),
        }
    } // :NOCOV_END
}
impl RequestBody {
    fn new(body: InnerBody) -> Self {
        Self(Mutex::new(Some(body)))
    }

    pub fn try_clone(&self, py: Python) -> PyResult<Self> {
        let body = match self.lock(py)?.as_ref() {
            Some(InnerBody::Bytes(bytes)) => InnerBody::Bytes(py.detach(|| bytes.clone())),
            Some(InnerBody::Stream(stream)) => InnerBody::Stream(Python::attach(|py| stream.try_clone(py))?),
            None => return Err(PyRuntimeError::new_err("Request body already consumed")),
        };
        Ok(Self::new(body))
    }

    pub fn take_inner(&self, py: Python) -> PyResult<Self> {
        Ok(Self::new(
            self.lock(py)?
                .take()
                .ok_or_else(|| PyRuntimeError::new_err("Request body already consumed"))?,
        ))
    }

    pub fn set_task_local(&self, py: Python, task_local: &OnceTaskLocal) -> PyResult<()> {
        match self.lock(py)?.as_mut() {
            Some(InnerBody::Bytes(_)) => Ok(()),
            Some(InnerBody::Stream(stream)) => stream.set_task_local(py, task_local),
            None => Err(PyRuntimeError::new_err("Request body already consumed")),
        }
    }

    #[allow(clippy::wrong_self_convention)]
    pub fn into_reqwest(&self, py: Python, is_blocking: bool) -> PyResult<reqwest::Body> {
        match self.lock(py)?.take() {
            Some(InnerBody::Bytes(bytes)) => Ok(reqwest::Body::from(bytes)),
            Some(InnerBody::Stream(stream)) => stream.into_reqwest(is_blocking),
            None => Err(PyRuntimeError::new_err("Request body already consumed")),
        }
    }

    fn lock(&self, py: Python) -> PyResult<MutexGuard<'_, Option<InnerBody>>> {
        self.0
            .lock_py_attached(py)
            .map_err(|_| PyRuntimeError::new_err("RequestBody mutex poisoned"))
    }
}
impl From<Bytes> for RequestBody {
    fn from(bytes: Bytes) -> Self {
        Self::new(InnerBody::Bytes(bytes))
    }
}

enum InnerBody {
    Bytes(Bytes),
    Stream(BodyStream),
}
