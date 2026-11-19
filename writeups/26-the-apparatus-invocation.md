# The Apparatus, Invocation

**Misc · Wave 1 · 101 pts**

A web page: 49 candles in a 7×7 grid. Pressing one "stirs the four cardinal
neighbors equally." Snuff them all and the apparatus speaks its name.
"The order does not matter, only the set."

This is **Lights Out**. Order-independent, toggle-based → solve over GF(2).

## Model

Each press is a vector over GF(2): pressing cell `i` flips `i` and its ≤4
orthogonal neighbors. Let `A` be the 49×49 toggle matrix (column `i` = cells
flipped by pressing `i`), `b` the initial lit vector. Solve `A·x = b`; `x` is
the press set.

```python
# build A, then Gaussian elimination over GF(2) on [A | b]
# x[i] == 1  => press cell i
```

For the team's board, the solution was a set of 28 presses, verified to clear
the whole grid.

## Doing it without eyeballing

Rather than trust a screenshot read, a browser-console script reads the live
board straight from the DOM (lit detection via computed-style luminance),
solves `A·x=b`, and clicks the solution cells:

```javascript
// read 49 cells row-major, detect lit, solve GF(2), click x==1 cells
```

The board the DOM reported matched the hand-read solve; the self-reading
script removes any transcription error.

## Flag

Revealed on the page once all candles are dark (per-team).

## Lesson

"Only the set matters" is the whole hint — it tells you presses commute, so the
board is a linear system over GF(2), not a search.
