use std::future::Future;

/// `AsyncRuntime` abstracts over various Rust's async runtimes with minimal interface.
pub trait AsyncRuntime {
    fn spawn<F>(&self, future: F)
    where
        F: Future + Send + 'static,
        F::Output: Send + 'static;
}

impl AsyncRuntime for tokio::runtime::Handle {
    fn spawn<F>(&self, future: F)
    where
        F: Future + Send + 'static,
        F::Output: Send + 'static,
    {
        tokio::runtime::Handle::spawn(self, future);
    }
}
