// SPDX-License-Identifier: Apache-2.0
// eBPF probe for tracking process memory access and debugging (sys_enter_ptrace).
// Emits kernel-level process access events matching ADAPT BlueTeam sensor criteria:
// detects credential dumping or injection into sensitive processes (e.g. lsass / ptrace access 0x1400).

#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

#define TASK_COMM_LEN 16

struct ptrace_event_t {
    u32 pid;
    u32 target_pid;
    u32 request;
    u64 addr;
    char comm[TASK_COMM_LEN];
};

BPF_PERF_OUTPUT(ptrace_events);

/**
 * Trace sys_enter_ptrace to identify process injection or memory scraping attempts.
 */
int trace_sys_enter_ptrace(struct tracepoint__syscalls__sys_enter_ptrace *ctx) {
    struct ptrace_event_t event = {};
    u64 pid_tgid = bpf_get_current_pid_tgid();
    event.pid = pid_tgid >> 32;

    bpf_get_current_comm(&event.comm, sizeof(event.comm));

    event.request = (u32)ctx->request;
    event.target_pid = (u32)ctx->pid;
    event.addr = (u64)ctx->addr;

    ptrace_events.perf_submit(ctx, &event, sizeof(event));
    return 0;
}
