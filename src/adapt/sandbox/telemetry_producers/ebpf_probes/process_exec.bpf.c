// SPDX-License-Identifier: Apache-2.0
// eBPF probe for tracking process execution (sys_enter_execve).
// Emits kernel-level process creation events matching ADAPT BlueTeam sensor criteria:
// detects /bin/sh, /bin/bash, powershell, pwsh, kerberoast, mimikatz.

#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <linux/fs.h>

#define MAX_FILENAME_LEN 256
#define MAX_ARGS_LEN 512
#define TASK_COMM_LEN 16

struct exec_event_t {
    u32 pid;
    u32 ppid;
    u32 uid;
    char comm[TASK_COMM_LEN];
    char filename[MAX_FILENAME_LEN];
    char args[MAX_ARGS_LEN];
};

BPF_PERF_OUTPUT(exec_events);

/**
 * Trace sys_enter_execve to capture newly spawned processes in the sandbox.
 */
int trace_sys_enter_execve(struct tracepoint__syscalls__sys_enter_execve *ctx) {
    struct exec_event_t event = {};
    u64 pid_tgid = bpf_get_current_pid_tgid();
    event.pid = pid_tgid >> 32;
    event.uid = bpf_get_current_uid_gid();

    struct task_struct *task = (struct task_struct *)bpf_get_current_task();
    event.ppid = task->real_parent->tgid;

    bpf_get_current_comm(&event.comm, sizeof(event.comm));

    // Read binary path
    if (ctx->filename) {
        bpf_probe_read_user_str(&event.filename, sizeof(event.filename), ctx->filename);
    }

    // Read first argument string if available
    const char *const *argv = (const char *const *)ctx->argv;
    if (argv) {
        const char *arg0 = NULL;
        bpf_probe_read_user(&arg0, sizeof(arg0), &argv[0]);
        if (arg0) {
            bpf_probe_read_user_str(&event.args, sizeof(event.args), arg0);
        }
    }

    exec_events.perf_submit(ctx, &event, sizeof(event));
    return 0;
}
