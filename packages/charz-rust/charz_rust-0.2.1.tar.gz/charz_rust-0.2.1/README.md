# Charz Rust

Blazingly fast speed-ups for `charz`

This addon module is used to improve performance of certain tasks in `charz`.
Uses `Rust` and `abi3`.

## Example

Substituting `charz.Screen` with a faster `charz_rust.RustScreen`

```python
from charz import Engine, ...
from charz_rust import RustScreen


class MyGame(Engine):
    screen = RustScreen()  # You can configure the screen,
                           # just like you would with `charz.Screen`
```

## License

MIT
