# ebpf_probes/

The actual eBPF programs attached inside sandbox containers, emitting
kernel-level events. These are typically C (`.bpf.c`) sources compiled with
`clang`/`bpftool`, loaded by the telemetry container at startup -- not Python
modules, hence no `__init__.py` here.
