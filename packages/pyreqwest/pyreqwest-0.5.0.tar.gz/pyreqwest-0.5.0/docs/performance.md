### Async runtime

Reqwest uses the `tokio` async runtime, so `pyreqwest` does as well. By default, the library runs on a global
single-threaded runtime chosen for simplicity and performance, which is sufficient for most use cases.
If needed, you can provide a dedicated `tokio` runtime via `ClientBuilder.runtime(Runtime)`.

### Buffer protocol and zero-copying

Library makes extensive use of Python buffer protocol to avoid unnecessary copying of data.
For example, request bodies are returned as `pyreqwest.bytes.Bytes` type. This is a `bytes`-like type that implements
the buffer protocol. You can pass the data to other libraries and functions without copying via `memoryview(Bytes)`.
Converting to `bytes`/`bytearray` happens via `bytes(Bytes)` which copies the underlying buffer.

Many `copy()` operations provided by the library create a zero-copy view of the underlying data (e.g. `Request.copy()`),
enabling efficient request retrying (when done e.g. via a middleware).

Library usually transfers ownership of its internal data structures between different functions calls,
such as those sending requests or builders. Therefore, some instance become usable after usage. For example, after
calling `Request.send()`, the `Request` instance is no longer usable.

### GIL releasing

Most operations release GIL, especially those doing any I/O operations. Also, various parsers release GIL such as JSON
and text decoding.

### Python 3.13+ free threading

Library supports Python 3.13+ free threading.

Following classes are thread-safe to use across multiple threads: `Client`, `SyncClient`, `CookieStore`.
These do not require additional locking or synchronization. Multiple requests can be started by different threads
concurrently.

Also, simple types and immutable types like `Url`, `HeaderMap`, `Bytes`, `Mime`, `Cookie` are thread-safe.

Builder classes are not thread-safe and should not be shared across threads.
(For example `ClientBuilder` and `SyncClientBuilder`.)
Multiple threads should not mutate the same builder object concurrently.

Also, request and response types are not thread-safe.
(For example `ConsumedRequest`, `Response`, `SyncConsumedRequest`, `SyncResponse`.)
Multiple threads should not read or write to the same request or response object concurrently.
