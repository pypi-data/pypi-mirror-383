import argparse, sys, requests
from . import __version__
from .adapters.fortigate import FortiGateClient
from .commands import register_all
from .commands.quarantine import register_quarantine_native
from .utils import print_json

def main():
    ap = argparse.ArgumentParser(description="FortiGate Policy & Address Toolkit")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    ap.add_argument("--host", required=True, help="e.g. https://10.0.0.1:10443")
    ap.add_argument("--token", required=True, help="API token")
    ap.add_argument("--vdom", default=None, help="VDOM name (e.g. root)")
    ap.add_argument("--insecure", action="store_true", help="Disable SSL verification")

    sub = ap.add_subparsers(dest="cmd")

    # 现有所有老命令
    register_all(sub)

    # 新增：原生隔离子命令
    register_quarantine_native(sub)

    args = ap.parse_args()
    if not hasattr(args, "_handler"):
        ap.print_help(); sys.exit(2)

    client = FortiGateClient(args.host, args.token, args.vdom, verify_ssl=not args.insecure)
    try:
        rc = args._handler(client, args)
        sys.exit(rc if isinstance(rc, int) else 0)
    except requests.exceptions.SSLError as e:
        print_json({"error": "SSL error. Put --insecure BEFORE the subcommand.", "detail": str(e)}); sys.exit(1)
    except requests.exceptions.RequestException as e:
        print_json({"error": "HTTP error", "detail": str(e)}); sys.exit(1)
    except Exception as e:
        print_json({"error": str(e)}); sys.exit(1)
