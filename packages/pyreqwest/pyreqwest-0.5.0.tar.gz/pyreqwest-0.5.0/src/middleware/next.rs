use crate::allow_threads::AllowThreads;
use crate::asyncio::{PyCoroWaiter, TaskLocal, py_coro_waiter};
use crate::request::Request;
use crate::response::{BaseResponse, Response, SyncResponse};
use pyo3::coroutine::CancelHandle;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::{PyTraverseError, PyVisit};
use std::sync::Arc;

pub struct NextInner {
    middlewares: Option<Arc<Vec<Py<PyAny>>>>,
    current: usize,
    override_middlewares: Option<Vec<Py<PyAny>>>,
}

#[pyclass(frozen)]
pub struct Next {
    inner: NextInner,
    task_local: TaskLocal,
}
#[pyclass]
pub struct SyncNext(NextInner);

#[pymethods]
impl Next {
    pub async fn run(&self, request: Py<PyAny>, #[pyo3(cancel_handle)] cancel: CancelHandle) -> PyResult<Py<Response>> {
        let resp = self.run_inner(&request, cancel).await?;
        Python::attach(|py| Response::new_py(py, resp))
    }

    // :NOCOV_START
    pub fn __traverse__(&self, visit: PyVisit<'_>) -> Result<(), PyTraverseError> {
        self.inner.__traverse__(&visit)?;
        self.task_local.__traverse__(&visit)
    } // :NOCOV_END
}
impl Next {
    pub fn new(inner: NextInner, task_local: TaskLocal) -> PyResult<Self> {
        Ok(Next { inner, task_local })
    }

    pub async fn run_inner(&self, request: &Py<PyAny>, cancel: CancelHandle) -> PyResult<BaseResponse> {
        if let Some(middleware) = self.inner.current_middleware()? {
            let next_waiter = Python::attach(|py| self.call_next(py, middleware, request, cancel))?;
            let resp = AllowThreads(next_waiter).await?;
            Python::attach(|py| {
                resp.into_bound(py)
                    .downcast_into_exact::<Response>()?
                    .into_super()
                    .try_borrow_mut()?
                    .take_inner()
            })
        } else {
            // No more middleware, execute the request
            Request::spawn_request(request, cancel).await
        }
    }

    fn call_next(
        &self,
        py: Python,
        middleware: &Py<PyAny>,
        request: &Py<PyAny>,
        cancel: CancelHandle,
    ) -> PyResult<PyCoroWaiter> {
        let task_local = self.task_local.clone_ref(py)?;
        let next = Next {
            inner: self.inner.create_next(py)?,
            task_local,
        };

        let coro = middleware.bind(py).call1((request, next))?;
        py_coro_waiter(coro, &self.task_local, Some(cancel))
    }
}

#[pymethods]
impl SyncNext {
    pub fn run(&self, request: &Bound<PyAny>) -> PyResult<Py<SyncResponse>> {
        let resp = self.run_inner(request)?;
        Python::attach(|py| SyncResponse::new_py(py, resp))
    }

    // :NOCOV_START
    pub fn __traverse__(&self, visit: PyVisit<'_>) -> Result<(), PyTraverseError> {
        self.0.__traverse__(&visit)
    }

    pub fn __clear__(&mut self) {
        self.0.__clear__()
    } // :NOCOV_END
}
impl SyncNext {
    pub fn new(inner: NextInner) -> PyResult<Self> {
        Ok(SyncNext(inner))
    }

    pub fn run_inner(&self, request: &Bound<PyAny>) -> PyResult<BaseResponse> {
        if let Some(middleware) = self.0.current_middleware()? {
            let resp = self.call_next(middleware, request)?;
            resp.downcast_into_exact::<SyncResponse>()?
                .into_super()
                .try_borrow_mut()?
                .take_inner()
        } else {
            // No more middleware, execute the request
            Request::blocking_spawn_request(request.downcast::<Request>()?)
        }
    }

    fn call_next<'py>(&self, middleware: &Py<PyAny>, request: &Bound<'py, PyAny>) -> PyResult<Bound<'py, PyAny>> {
        let py = request.py();
        let next = SyncNext(self.0.create_next(py)?);
        middleware.bind(py).call1((request, next))
    }
}

impl NextInner {
    pub fn new(middlewares: Arc<Vec<Py<PyAny>>>) -> PyResult<Self> {
        if middlewares.is_empty() {
            return Err(PyRuntimeError::new_err("Expected at least one middleware"));
        }
        Ok(NextInner {
            middlewares: Some(middlewares),
            current: 0,
            override_middlewares: None,
        })
    }

    fn current_middleware(&self) -> PyResult<Option<&Py<PyAny>>> {
        if let Some(override_middlewares) = self.override_middlewares.as_ref() {
            Ok(override_middlewares.get(self.current))
        } else {
            Ok(self
                .middlewares
                .as_ref()
                .ok_or_else(|| PyRuntimeError::new_err("Expected middlewares"))?
                .get(self.current))
        }
    }

    fn create_next(&self, py: Python) -> PyResult<NextInner> {
        Ok(NextInner {
            middlewares: self.middlewares.clone(),
            current: self.current + 1,
            override_middlewares: self
                .override_middlewares
                .as_ref()
                .map(|m| m.iter().map(|v| v.clone_ref(py)).collect()),
        })
    }

    pub fn add_middleware(&mut self, middleware: Bound<PyAny>) -> PyResult<()> {
        if let Some(orig) = self.middlewares.take() {
            assert!(self.override_middlewares.is_none());
            self.override_middlewares = Some(orig.iter().map(|m| m.clone_ref(middleware.py())).collect());
        }
        self.override_middlewares
            .as_mut()
            .ok_or_else(|| PyRuntimeError::new_err("Expected override_middlewares"))?
            .push(middleware.unbind());
        Ok(())
    }

    pub fn clone_ref(&self, py: Python) -> Self {
        let override_middlewares = self
            .override_middlewares
            .as_ref()
            .map(|m| m.iter().map(|v| v.clone_ref(py)).collect::<Vec<_>>());

        NextInner {
            middlewares: self.middlewares.clone(),
            current: self.current,
            override_middlewares,
        }
    }

    // :NOCOV_START
    pub fn __traverse__(&self, visit: &PyVisit<'_>) -> Result<(), PyTraverseError> {
        if let Some(middlewares) = &self.middlewares {
            for mw in middlewares.iter() {
                visit.call(mw)?;
            }
        }
        if let Some(middlewares) = &self.override_middlewares {
            for mw in middlewares.iter() {
                visit.call(mw)?;
            }
        }
        Ok(())
    }

    pub fn __clear__(&mut self) {
        self.middlewares = None;
        self.override_middlewares = None;
    } // :NOCOV_END
}
