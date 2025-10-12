## `blindfile`

![blindfile logo](docs/images/logo.png)


The virtual blindfold to make truly unbiased file comparisons ⚖️.


## Installation

Install using either [`uv`](https://github.com/astral-sh/uv), [`pipx`](https://github.com/pypa/pipx) or [`pip`](https://github.com/pypa/pip).

```
# install as a tool (recommended)...
$ uv install tool blindfile
$ pipx install blindfile

# or as a a package
$ uv add blindfile
$ pip install blindfile
```

## Usage example

Let's say you want to compare some wav files: `take1.wav`, `take2.wav` and `take3.wav`.
1. **`cover` (hide your filenames)**
   ```
   $ blindfile cover '*.wav'
   __blindfile__/contemporary-tree.wav
   __blindfile__/generous-blade.wav
   __blindfile__/caramel-nut.wav
   ```


1. **compare your files**

   Open files listed by `cover` and compare them. In our example - get your headphones and decide which file sounds best 🎧 !

1. **`uncover` (reveal the originals)**
 
   When you're ready to learn which file is which, run:

   ```
   $ blindfile uncover
   __blindfile__/contemporary-tree.wav -> take2.wav
   __blindfile__/generous-blade.wav -> take3.wav
   __blindfile__/caramel-nut.wav -> take1.wav
   ```
