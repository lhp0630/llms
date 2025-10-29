




```python
from contextlib import contextmanager
import json
from typing import Any, ContextManager, Generator, Protocol, runtime_checkable
from nebula3.gclient.net import ConnectionPool, Session
from nebula3.Config import Config


def _init_pool(host: str, port: int) -> ConnectionPool:
    config = Config()
    config.max_connection_pool_size = 2
    connection_pool = ConnectionPool()
    assert connection_pool.init([(host, port)], config)
    return connection_pool


connection_pool = _init_pool(host="127.0.0.1", port=9669)


@contextmanager
def _acquire_session(user: str, password: str, space: str):
    s: Session | None = None
    try:
        s = connection_pool.get_session(user, password)
        s.execute(f"USE {space}")
        yield s
    finally:
        if s:
            s.release()


@runtime_checkable
class SessionProvider(Protocol):
    def get_session(self) -> ContextManager[Session]: ...


class NebulaKnowledgeGraph:
    def __init__(self, sess: Session | SessionProvider, **kwargs: dict[str, Any]):
        super().__init__()

        self.session = sess

    @contextmanager
    def _get_active_session(self) -> Generator[Session, None, None]:
        if isinstance(self.session, SessionProvider):
            # If session is a Provider, obtain session using its context manager (auto release).
            with self.session.get_session() as s:
                yield s
        else:
            # We directly yield the provided session instance here. Since it is passed in from outside,
            # its lifecycle should be managed by the caller, and it should not be released internally.
            yield self.session

    def execute_query(self, query: str) -> list[dict[str, Any]] | None:
        with self._get_active_session() as s:
            try:
                result_json = s.execute_json(query)
                data = json.loads(result_json)
                if "results" in data and len(data["results"]) > 0:
                    return data["results"][0]["data"]
                return None
            except Exception as e:
                msg = f"Query execution failed: {e}"
                raise ValueError(msg) from e


if __name__ == "__main__":
    c = _acquire_session(user="root", password="root", space="demo")

    with c as s:
        n = NebulaKnowledgeGraph(s)
        r = n.execute_query('MATCH (x) WHERE x["name"] == "售电分析" RETURN x')
        print(r)
```
