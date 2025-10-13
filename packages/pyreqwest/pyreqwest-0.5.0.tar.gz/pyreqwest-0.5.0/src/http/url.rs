use crate::internal::types::QueryParams;
use pyo3::basic::CompareOp;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{PyDict, PyIterator, PyList, PyString};
use pyo3::{IntoPyObjectExt, intern};
use serde::Serialize;
use std::hash::{DefaultHasher, Hash, Hasher};
use std::net::IpAddr;
use std::str::FromStr;

#[pyclass(frozen)]
pub struct Url {
    url: url::Url,
    query: PyOnceLock<Vec<(Py<PyString>, Py<PyString>)>>,
}

#[pymethods]
impl Url {
    #[new]
    fn new_py(url: UrlType) -> Self {
        Url::new(url.0)
    }

    #[staticmethod]
    pub fn parse(url: UrlType) -> Self {
        Url::new(url.0)
    }

    #[staticmethod]
    fn parse_with_params(url: UrlType, query: QueryParams) -> PyResult<Self> {
        let mut url = url.0;
        Self::extend_query_inner(&mut url, Some(query))?;
        Ok(Url::from(url))
    }

    #[staticmethod]
    pub fn is_valid(raw: &str) -> bool {
        url::Url::parse(raw).is_ok()
    }

    pub fn join(&self, input: &str) -> PyResult<Self> {
        let url = self.url.join(input).map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(Url::new(url))
    }

    fn make_relative(&self, base: UrlType) -> Option<String> {
        self.url.make_relative(&base.0)
    }

    #[getter]
    fn origin_ascii(&self) -> String {
        self.url.origin().ascii_serialization()
    }

    #[getter]
    fn origin_unicode(&self) -> String {
        self.url.origin().unicode_serialization()
    }

    #[getter]
    fn scheme(&self) -> &str {
        self.url.scheme()
    }

    #[getter]
    fn is_special(&self) -> bool {
        self.url.is_special()
    }

    #[getter]
    fn has_authority(&self) -> bool {
        self.url.has_authority()
    }

    #[getter]
    fn authority(&self) -> &str {
        self.url.authority()
    }

    #[getter]
    fn cannot_be_a_base(&self) -> bool {
        self.url.cannot_be_a_base()
    }

    #[getter]
    fn username(&self) -> &str {
        self.url.username()
    }

    #[getter]
    fn password(&self) -> Option<&str> {
        self.url.password()
    }

    #[getter]
    fn has_host(&self) -> bool {
        self.url.has_host()
    }

    #[getter]
    fn host_str(&self) -> Option<&str> {
        self.url.host_str()
    }

    #[getter]
    fn domain(&self) -> Option<&str> {
        self.url.domain()
    }

    #[getter]
    fn port(&self) -> Option<u16> {
        self.url.port()
    }

    #[getter]
    fn port_or_known_default(&self) -> Option<u16> {
        self.url.port_or_known_default()
    }

    #[getter]
    fn path(&self) -> &str {
        self.url.path()
    }

    #[getter]
    fn path_segments(&self) -> Option<Vec<&str>> {
        self.url.path_segments().map(|v| v.collect::<Vec<_>>())
    }

    #[getter]
    fn query_string(&self) -> Option<&str> {
        self.url.query()
    }

    #[getter]
    fn query_pairs<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        PyList::new(py, self.query_pairs_vec(py))
    }

    #[getter]
    fn query_dict_multi_value<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        let dict = PyDict::new(py);
        for (k, v) in self.query_pairs_vec(py) {
            match dict.get_item(k)? {
                None => dict.set_item(k, v)?,
                Some(existing) => match existing.downcast_into_exact::<PyList>() {
                    Ok(existing) => existing.append(v)?,
                    Err(err) => {
                        let existing = err.into_inner();
                        let existing = existing.downcast_exact::<PyString>()?;
                        dict.set_item(k, PyList::new(py, vec![existing, v.bind(py)])?)?;
                    }
                },
            }
        }
        Ok(dict)
    }

    #[getter]
    fn fragment(&self) -> Option<&str> {
        self.url.fragment()
    }

    fn with_query(&self, query: Option<QueryParams>) -> PyResult<Self> {
        let mut url = self.url.clone();
        url.set_query(None);
        Self::extend_query_inner(&mut url, query)?;
        Ok(Url::new(url))
    }

    fn extend_query(&self, query: Option<QueryParams>) -> PyResult<Self> {
        let mut url = self.url.clone();
        Self::extend_query_inner(&mut url, query)?;
        Ok(Url::new(url))
    }

    pub fn with_query_string(&self, query: Option<&str>) -> Self {
        let mut url = self.url.clone();
        url.set_query(query);
        Url::new(url)
    }

    fn with_path(&self, path: &str) -> Self {
        let mut url = self.url.clone();
        url.set_path(path);
        Url::new(url)
    }

    fn with_path_segments(&self, segments: Vec<String>) -> PyResult<Self> {
        let mut url = self.url.clone();
        {
            let mut path = url
                .path_segments_mut()
                .map_err(|_| PyValueError::new_err("cannot be base"))?;
            path.clear();
            path.extend(segments);
        }
        Ok(Url::new(url))
    }

    fn with_port(&self, port: Option<u16>) -> PyResult<Self> {
        let mut url = self.url.clone();
        url.set_port(port)
            .map_err(|_| PyValueError::new_err("cannot be base"))?;
        Ok(Url::new(url))
    }

    fn with_host(&self, host: Option<&str>) -> PyResult<Self> {
        let mut url = self.url.clone();
        url.set_host(host).map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(Url::new(url))
    }

    fn with_ip_host(&self, addr: &str) -> PyResult<Self> {
        let addr = IpAddr::from_str(addr).map_err(|e| PyValueError::new_err(e.to_string()))?;
        let mut url = self.url.clone();
        url.set_ip_host(addr)
            .map_err(|_| PyValueError::new_err("cannot be base"))?;
        Ok(Url::new(url))
    }

    fn with_username(&self, username: &str) -> PyResult<Self> {
        let mut url = self.url.clone();
        url.set_username(username)
            .map_err(|_| PyValueError::new_err("cannot be base"))?;
        Ok(Url::new(url))
    }

    fn with_password(&self, password: Option<&str>) -> PyResult<Self> {
        let mut url = self.url.clone();
        url.set_password(password)
            .map_err(|_| PyValueError::new_err("cannot be base"))?;
        Ok(Url::new(url))
    }

    fn with_scheme(&self, scheme: &str) -> PyResult<Self> {
        let mut url = self.url.clone();
        url.set_scheme(scheme)
            .map_err(|_| PyValueError::new_err("Invalid scheme"))?;
        Ok(Url::new(url))
    }

    fn with_fragment(&self, fragment: Option<&str>) -> Self {
        let mut url = self.url.clone();
        url.set_fragment(fragment);
        Url::new(url)
    }

    fn __copy__(&self) -> Self {
        Url::new(self.url.clone())
    }

    fn __truediv__(&self, other: &str) -> PyResult<Self> {
        self.join(other)
    }

    fn __str__<'py>(&self, py: Python<'py>) -> Bound<'py, PyString> {
        PyString::new(py, self.as_str())
    }

    fn __repr__(slf: Bound<Self>) -> PyResult<String> {
        let url_repr = slf.call_method0(intern!(slf.py(), "__str__"))?.repr()?;
        Ok(format!("Url({})", url_repr.to_str()?))
    }

    fn __hash__(&self) -> u64 {
        let mut hasher = DefaultHasher::new();
        self.url.hash(&mut hasher);
        hasher.finish()
    }

    fn __richcmp__<'py>(
        &self,
        py: Python<'py>,
        other: Bound<'py, PyAny>,
        op: CompareOp,
    ) -> PyResult<Bound<'py, PyAny>> {
        let Ok(other) = other.extract::<UrlType>() else {
            return self.__str__(py).rich_compare(other, op);
        };
        match op {
            CompareOp::Lt => self.url < other.0,
            CompareOp::Le => self.url <= other.0,
            CompareOp::Eq => self.url == other.0,
            CompareOp::Ne => self.url != other.0,
            CompareOp::Gt => self.url > other.0,
            CompareOp::Ge => self.url >= other.0,
        }
        .into_bound_py_any(py)
    }

    fn __len__(&self) -> usize {
        self.as_str().len()
    }

    fn __contains__(&self, item: &str) -> bool {
        self.as_str().contains(item)
    }

    fn __getitem__<'py>(&self, py: Python<'py>, k: Bound<'py, PyAny>) -> PyResult<Bound<'py, PyAny>> {
        self.__str__(py).get_item(k)
    }

    fn __iter__<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyIterator>> {
        self.__str__(py).try_iter()
    }
}
impl Url {
    fn new(url: url::Url) -> Self {
        Url {
            url,
            query: PyOnceLock::new(),
        }
    }

    fn parse_inner(url: &str) -> PyResult<url::Url> {
        url::Url::parse(url).map_err(|e| PyValueError::new_err(e.to_string()))
    }

    fn query_pairs_vec(&self, py: Python) -> &Vec<(Py<PyString>, Py<PyString>)> {
        self.query.get_or_init(py, || {
            self.url
                .query_pairs()
                .map(|(k, v)| {
                    let k = PyString::new(py, &k);
                    let v = PyString::new(py, &v);
                    (k.unbind(), v.unbind())
                })
                .collect()
        })
    }

    fn extend_query_inner(url: &mut url::Url, query: Option<QueryParams>) -> PyResult<()> {
        if let Some(query) = query.map(|q| q.0) {
            let mut pairs = vec![];
            for (key, val) in query.iter() {
                match val.0.as_array() {
                    Some(arr) => pairs.extend(arr.iter().map(|v| (key, v))),
                    None => pairs.push((key, &val.0)),
                }
            }

            pairs
                .serialize(serde_urlencoded::Serializer::new(&mut url.query_pairs_mut()))
                .map_err(|e| PyValueError::new_err(e.to_string()))?;
        }
        Ok(())
    }

    pub fn as_str(&self) -> &str {
        self.url.as_str()
    }
}
impl From<reqwest::Url> for Url {
    fn from(value: reqwest::Url) -> Self {
        Url::new(value)
    }
}
impl From<UrlType> for Url {
    fn from(value: UrlType) -> Self {
        Url::new(value.0)
    }
}
impl From<Url> for reqwest::Url {
    fn from(val: Url) -> Self {
        val.url
    }
}
impl Clone for Url {
    fn clone(&self) -> Self {
        Url::new(self.url.clone())
    }
}

pub struct UrlType(pub url::Url);
impl<'py> FromPyObject<'py> for UrlType {
    fn extract_bound(ob: &Bound<'py, PyAny>) -> PyResult<Self> {
        if let Ok(url) = ob.downcast_exact::<Url>() {
            return Ok(UrlType(url.try_borrow()?.url.clone()));
        }
        if let Ok(str) = ob.extract::<&str>() {
            return Ok(UrlType(Url::parse_inner(str)?));
        }
        Ok(UrlType(Url::parse_inner(ob.str()?.to_str()?)?))
    }
}
