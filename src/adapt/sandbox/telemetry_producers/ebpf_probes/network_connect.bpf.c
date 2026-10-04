// SPDX-License-Identifier: Apache-2.0
// eBPF probe for tracking TCP connection attempts (sys_enter_connect / tcp_v4_connect).
// Emits kernel-level network connection events matching ADAPT BlueTeam sensor criteria:
// detects connection attempts to Kerberos (port 88), LDAP (port 389), SMB (port 445).

#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <linux/in.h>

#define TASK_COMM_LEN 16

struct connect_event_t {
    u32 pid;
    u32 saddr;
    u32 daddr;
    u16 sport;
    u16 dport;
    u16 proto;
    char comm[TASK_COMM_LEN];
};

BPF_PERF_OUTPUT(connect_events);

/**
 * Trace TCP IPv4 connection attempts.
 */
int trace_tcp_v4_connect(struct pt_regs *ctx, struct sock *sk) {
    struct connect_event_t event = {};
    u64 pid_tgid = bpf_get_current_pid_tgid();
    event.pid = pid_tgid >> 32;

    bpf_get_current_comm(&event.comm, sizeof(event.comm));

    u16 dport = 0;
    bpf_probe_read_kernel(&dport, sizeof(dport), &sk->__sk_common.skc_dport);
    event.dport = ntohs(dport);

    // Filter or highlight key enterprise ports: 88 (Kerberos), 389 (LDAP), 445 (SMB)
    bpf_probe_read_kernel(&event.saddr, sizeof(event.saddr), &sk->__sk_common.skc_rcv_saddr);
    bpf_probe_read_kernel(&event.daddr, sizeof(event.daddr), &sk->__sk_common.skc_daddr);
    bpf_probe_read_kernel(&event.sport, sizeof(event.sport), &sk->__sk_common.skc_num);
    event.proto = IPPROTO_TCP;

    connect_events.perf_submit(ctx, &event, sizeof(event));
    return 0;
}
