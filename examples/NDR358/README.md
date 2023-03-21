# Notes

MTU size for the Recieveing computer and interfaces should be 9000 on any interface that the V49 will be streamed to.

Secondly, tuning the RX ring buffer and interrupt coalescing is needed to make sure the host can keep up with multiple streams.
