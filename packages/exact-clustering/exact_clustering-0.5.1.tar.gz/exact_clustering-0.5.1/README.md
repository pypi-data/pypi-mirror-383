![PyPI - Version](https://img.shields.io/pypi/v/exact-clustering)

Low-effort way of calling the rust-crate [`exact-clustering`](https://github.com/lumi-a/exact-clustering) from Python. 

```sh
pip install exact-clustering
```

Consult [docs.rs](https://docs.rs/exact-clustering) for more extensive documentation.

```py
from exact_clustering import *

weighted_points = [
    (1.0, [0, 0]),
    (1.0, [1, 0]),
    (3.0, [0, 2]),
]

print(
    weighted_continuous_kmeans_price_of_hierarchy(
        weighted_points
    )
)
# 1.0
```

View provided methods via `help(exact_clustering)` in the python-repl or take a look at `exact_clustering.pyi`. At time of writing, they are:

```py
class KMeans:
    def __new__(cls, data: Sequence[Sequence[float]]) -> KMeans: ...
    def price_of_hierarchy(self) -> float: ...
    def price_of_greedy(self) -> float: ...

class KMedianL1:
    def __new__(cls, data: Sequence[Sequence[float]]) -> KMedianL1: ...
    def price_of_hierarchy(self) -> float: ...
    def price_of_greedy(self) -> float: ...

class KMedianL2:
    def __new__(cls, data: Sequence[Sequence[float]]) -> KMedianL2: ...
    def price_of_hierarchy(self) -> float: ...
    def price_of_greedy(self) -> float: ...

class KMedianL2Squared:
    def __new__(cls, data: Sequence[Sequence[float]]) -> KMedianL2Squared: ...
    def price_of_hierarchy(self) -> float: ...
    def price_of_greedy(self) -> float: ...

class UnweightedKMedianL1:
    def __new__(cls, data: Sequence[tuple[float, Sequence[float]]]) -> UnweightedKMedianL1: ...
    def price_of_hierarchy(self) -> float: ...
    def price_of_greedy(self) -> float: ...

class UnweightedKMedianL2:
    def __new__(cls, data: Sequence[tuple[float, Sequence[float]]]) -> UnweightedKMedianL2: ...
    def price_of_hierarchy(self) -> float: ...
    def price_of_greedy(self) -> float: ...

class UnweightedKMedianL2Squared:
    def __new__(cls, data: Sequence[tuple[float, Sequence[float]]]) -> UnweightedKMedianL2Squared: ...
    def price_of_hierarchy(self) -> float: ...
    def price_of_greedy(self) -> float: ...

class WeightedKMeans:
    def __new__(cls, data: Sequence[tuple[float, Sequence[float]]]) -> WeightedKMeans: ...
    def price_of_hierarchy(self) -> float: ...
    def price_of_greedy(self) -> float: ...
```

## License

Licensed under either of

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.


## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in the work by you, as defined in the Apache-2.0 license, shall be
dual licensed as above, without any additional terms or conditions.
