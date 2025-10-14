from ..utils import print_json

def register_quarantine_native(subparsers):
    ql = subparsers.add_parser("quarantine-native-list", help="List quarantined IPs (native)")
    ql.set_defaults(_handler=_handle_qlist)

    qa = subparsers.add_parser("quarantine-native-add", help="Add IP(s) to quarantine (native)")
    qa.add_argument("--ip", help="single IP")
    qa.add_argument("--ips", help="comma separated IPs, e.g. 1.2.3.4,5.6.7.8")
    qa.add_argument("--ttl", type=int, default=None, help="TTL seconds")
    qa.set_defaults(_handler=_handle_qadd)

    qr = subparsers.add_parser("quarantine-native-remove", help="Remove IP(s) from quarantine (native)")
    qr.add_argument("--ip", help="single IP")
    qr.add_argument("--ips", help="comma separated IPs")
    qr.set_defaults(_handler=_handle_qremove)

    qc = subparsers.add_parser("quarantine-native-clear", help="Clear quarantine list (native)")
    qc.set_defaults(_handler=_handle_qclear)


def _handle_qlist(client, args):
    out = client.quarantine_list_native()
    print_json(out); return 0

def _handle_qadd(client, args):
    ips = []
    if getattr(args, "ip", None):
        ips.append(args.ip)
    if getattr(args, "ips", None):
        ips.extend([x.strip() for x in args.ips.split(",") if x.strip()])
    if not ips:
        print_json({"error": "Please provide --ip or --ips"}); return 2

    out = client.quarantine_add_native(ips, ttl=args.ttl)  # 只传 ip/ttl
    print_json(out); return 0

def _handle_qremove(client, args):
    ips = []
    if getattr(args, "ip", None):
        ips.append(args.ip)
    if getattr(args, "ips", None):
        ips.extend([x.strip() for x in args.ips.split(",") if x.strip()])
    if not ips:
        print_json({"error": "Please provide --ip or --ips"}); return 2

    out = client.quarantine_remove_native(ips)
    print_json(out); return 0

def _handle_qclear(client, args):
    out = client.quarantine_clear_native()
    print_json(out); return 0
