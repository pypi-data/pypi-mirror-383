# FortiGate Policy & Address Toolkit — **README (v1.1.3)**

A single-file Python CLI that talks to FortiGate’s REST API to manage **policies**, **addresses**, **address groups**, and **virtual IPs (VIPs)** — plus a few productivity helpers (smart grouping, bulk attach, quick search).

> Tested against FortiOS **7.4.4** and **7.2.7**. The script includes compatibility shims for common response/payload differences between these versions.

## ✨ Highlights

- **Policies**: inspect by ID/name, search, create, update, mutate `srcaddr`/`dstaddr` quickly, attach address-group families.
- **Addresses**: full CRUD, JSON and no-JSON shortcuts, resilient subnet handling.
- **Address Groups**: full CRUD, validate members, add/remove members, “find groups containing X”.
- **Smart chunking**: keep each group ≤ **255** members; auto-create `-2`, `-3`, … suffix groups.
- **VIPs (Virtual IPs)**: list/search/get/create/update/delete. Supports **1:1 static NAT** and **port forward** (tcp/udp/sctp). FortiOS 7.2/7.4 payload compatibility built in.
- **Robustness**: VDOM fallback for `424`, graceful retries for common 5xx validation shapes, “remove `all` when mixed” safeguard.

## 🧩 Requirements

- Python **3.8+**

- Packages: `requests`, `urllib3`

  ```
  pip install requests urllib3
  ```

No other third-party deps. `ipaddress` is stdlib.

## 🔐 Authentication & Connectivity

- Pass your API token with **both** headers and query: the tool sets `Authorization: Bearer`, `X-Auth-Token`, and `?access_token=...` automatically. It's recommended to grand the API administrator permission.
- **Self-signed certs**: use `--insecure` (or import the FortiGate CA into your OS trust store).

> ❗ Place `--insecure` **before** the subcommand, otherwise it won’t apply.

------

## Example 1:  remove IPs from ip_addr_group with prefix "Blacklist_"

```python
from netknife.adapters.fortigate import FortiGateClient
import ipaddress
import re

BLACK_PREFIX = "Blacklist_"

###
The fw_map you pass in only needs to include host/token/vdom (policy information is not required).
If your address objects are indeed uniformly named as BAN-<ip>, this code will first try to use that name; if there are exceptions in naming, it will fall back to searching the full address list to find the object name matching that /32 and remove it.
If you also want to delete the address object itself (after it has been successfully removed from the group and is no longer referenced), you can add one more step: check the reference relations and then call client.delete_address(name). If you’d like, I can also integrate this “orphan object cleanup” into the process.
###

# --------- helpers ----------
def _names(lst):
    out = []
    for x in (lst or []):
        out.append(x.get("name") if isinstance(x, dict) else x)
    return out

def _valid_ip_list(ips):
    ok, bad = [], []
    for ip in sorted(set(map(str, ips))):
        try:
            ipaddress.ip_address(ip)
            ok.append(ip)
        except Exception:
            bad.append(ip)
    return ok, bad

def _address_matches_ip(addr: dict, ip: str) -> bool:
    if not isinstance(addr, dict) or (addr.get("type") != "ipmask"):
        return False
    subnet = addr.get("subnet")
    if isinstance(subnet, str):
        # "A.B.C.D MASK"
        return subnet.strip().startswith(ip + " ")
    if isinstance(subnet, list) and len(subnet) == 2:
        return str(subnet[0]) == ip and str(subnet[1]) in ("255.255.255.255", "255.255.255.255 ")
    return False

def _candidate_addr_names_for_ip(client: FortiGateClient, ip: str):
    """
    Return a list of address object names that should be removed.
    Give priority to BAN-<ip>; if it does not exist, then scan the address library for an object name matching the /32.
    """
    names = []
    ban_name = f"BAN-{ip}"
    a = client.get_address(ban_name)
    if a:
        names.append(ban_name)
    else:
        # Scan all address objects and find the one whose /32 equals the IP.
        for addr in client.list_addresses():
            if _address_matches_ip(addr, ip):
                nm = addr.get("name")
                if nm:
                    names.append(nm)
    # remove duplicate
    return sorted(set(names))

def _blacklist_groups(client: FortiGateClient):
    """
    Return all address group names that start with Blacklist_ (including shards, such as Blacklist_info-2).
    """
    groups = client.list_addrgrps()
    pat = re.compile(rf"^{re.escape(BLACK_PREFIX)}.*$")
    return sorted([g.get("name") for g in groups if g.get("name") and pat.match(g["name"])])

def _verify_member_not_in_group(client: FortiGateClient, group_name: str, member_name: str) -> bool:
    g = client.get_addrgrp(group_name)
    mems = set(_names(g.get("member"))) if g else set()
    return member_name not in mems

# --------- main API ----------
def unban_ips(fw_map, ips):
    """
    Remove the address member corresponding to the given IP from all address groups whose names start with Blacklist_.
    The fw_map structure is the same as in ban_ip, but here it only requires host/token/vdom.
    Return: (all_ok: bool, report: dict)
    """
    valid_ips, invalid_ips = _valid_ip_list(ips)
    if not valid_ips:
        return False, {"global_error": "no valid IPs", "invalid_ips": invalid_ips}

    overall_ok = True
    report = {"invalid_ips": invalid_ips, "devices": {}}

    for fw_name, cfg in fw_map.items():
        host  = cfg["host"]
        token = cfg["token"]
        vdom  = cfg.get("vdom")

        dev = {
            "groups": [],
            "ips": {},
            "errors": [],
            "ok": False,
        }
        report["devices"][fw_name] = dev

        client = FortiGateClient(host=host, token=token, vdom=vdom, verify_ssl=False)
        try:
            # 1) Find all groups starting with Blacklist_
            groups = _blacklist_groups(client)
            dev["groups"] = groups
            if not groups:
                dev["errors"].append("no Blacklist_* groups found")
                overall_ok = False
                continue

            # 2) Process each IP individually.
            for ip in valid_ips:
                ipres = {
                    "addr_candidates": [],
                    "per_group": [],   # [{group, attempted, removed, verified, note}]
                    "ok": False,
                }
                dev["ips"][ip] = ipres

                # 2.1 Parse the possible address object name(s).
                candidates = _candidate_addr_names_for_ip(client, ip)
                ipres["addr_candidates"] = candidates

                if not candidates:
                    # If there are no candidate object names, it means that the address library also has no address object for this IP; for the purpose of “removing a member,” treat it as already absent from all groups.
                    ipres["ok"] = True
                    continue

                # 2.2 Iterate over each group to perform removal and verification.
                group_all_ok = True
                for gname in groups:
                    # Only initiate a change if the group actually contains any of them.
                    g = client.get_addrgrp(gname)
                    cur = set(_names(g.get("member"))) if g else set()
                    targets = [nm for nm in candidates if nm in cur]

                    attempted = False
                    removed = False
                    verified = False
                    note = ""

                    if targets:
                        attempted = True
                        try:
                            # Use the library’s idempotent removal (you can also pass multiple at once).
                            client.remove_members_from_addrgrp(gname, targets)
                            # Verify that the removal was successful.
                            ok_now = all(_verify_member_not_in_group(client, gname, nm) for nm in targets)
                            removed = True
                            verified = ok_now
                            if not ok_now:
                                note = f"verify failed for {targets}"
                                group_all_ok = False
                                overall_ok = False
                        except Exception as e:
                            note = f"remove error: {e}"
                            group_all_ok = False
                            overall_ok = False
                    else:
                        note = "not in group"

                    ipres["per_group"].append({
                        "group": gname,
                        "attempted": attempted,
                        "removed": removed,
                        "verified": verified,
                        "note": note,
                    })

                ipres["ok"] = group_all_ok

            # 3) Device level OK?
            dev["ok"] = all(v.get("ok") for v in dev["ips"].values())
            if not dev["ok"]:
                overall_ok = False

        finally:
            try:
                client.session.close()
            except Exception:
                pass

    return overall_ok, report


# ---------------- demo ----------------
if __name__ == "__main__":
    fw_info = {
        "DC146": {
            "host": "https://10.146.1.1:10443",
            "token": "4Gps3rzsn5twq7js6ckyxzfQ",
            "vdom":  "SL-Internet",
        },
        "DC145": {
            "host": "https://10.1.1.1:10443",
            "token": "gqw4dnhhfscN67hddksc5mj",
            "vdom":  None,
        },
    }

    to_unban = ["1.1.1.1"]
    ok, rep = unban_ips(fw_info, to_unban)
    import json
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    print("ALL OK?", ok)

```



## ▶️ Quick Start

```
# Show version
python <SCRIPT>.py --version

# Inspect a policy by ID (with VDOM)
python <SCRIPT>.py --host https://10.1.1.1:10443 --token <TOKEN> --vdom test-vdom --insecure \
  policy-id --policy-id 209

# Search address groups by substring
python <SCRIPT>.py --host https://10.1.1.1:10443 --token <TOKEN> --vdom test-vdom --insecure \
  search-addrgrps --q Black
```

> Replace `<SCRIPT>.py` with your filename.
>  Windows CMD line continuation: use `^`; PowerShell: use backtick ``` or split lines.

------

## 🧭 Global CLI Syntax

```
python <SCRIPT>.py --host https://<ip>:<port> --token <TOKEN> [--vdom <VDOM>] [--insecure] <SUBCOMMAND> [OPTIONS]
```

**Global options**

- `--host` (required) – e.g. `https://10.1.1.1:10443`
- `--token` (required) – FortiGate API token
- `--vdom` (optional) – VDOM name (e.g. `test-vdom`)
- `--insecure` – disable SSL verification (self-signed)
- `--version` – print tool version (`v1.1.0`)

**Output**: JSON to stdout.
 **Exit codes**: `0` success, `1` runtime/API/SSL errors, `2` usage/help.

------

## 📚 Subcommands & Examples

### 1) Policies

#### Inspect / Search

```
# By ID
policy-id --policy-id 231

# By name
policy-name --policy-name "From-internet"

# Search by name substring
search-policies --q "blacklist"

# Find policies referencing a given object (addr/addrgrp/vip name)
find-policies-with --object-name "Blacklist"
```

#### Create

```
# JSON payload
create-policy --data @policy.json

# No-JSON “simple” creation
create-policy-simple \
  --name "From-internet-副本" \
  --srcintf "any" \
  --dstintf "any" \
  --srcaddr "blacklist-must-deny,blacklist-auto,Blacklist" \
  --dstaddr "all" \
  --service "ALL" \
  --action deny \
  --schedule always \
  --status enable \
  --logtraffic all \
  --comment "created by script"
```

`create-policy-simple` wraps comma-lists into FortiGate’s `[{ "name": ... }]` form automatically.

#### Update

```
# Full JSON replace/merge (FortiGate semantics)
update-policy --policy-id 263 --data @update.json

# Field-level updates (no JSON)
update-policy-fields --policy-id 263 \
  --srcaddr "Blacklist,Code_Group_BlackList" \
  --dstaddr "all" \
  --logtraffic all \
  --comment "updated by script"

# Enable/Disable (note spelling)
update-policy-fields --policy-id 263 --status disable
```

#### Quickly mutate src/dst address lists

```
# Add/remove names (addresses or groups)
policy-set-addrs --policy-id 263 --add-dst "Blacklist" --remove-src "OldGroup"
```

> Safeguard: if a list contains `all` **and** other members, the tool removes `all` to avoid FortiOS `500 -7`.
>  **VIP notice**: VIPs may be used **only** in **dstaddr** (destination). Using a VIP in `srcaddr` will fail (`500 -3`).

#### Attach an address-group family to a policy

```
# Will attach base and its -2/-3/... siblings (if present)
attach-grps-to-policy --policy-id 263 --base-name "Blacklist" --direction dst
```

------

### 2) Addresses

```
# List (brief)
list-addresses

# Search by substring
search-addresses --q "BAN-"

# Get one (full)
get-address --name "crl.pki.goog"

# Create (JSON)
create-address --data '{"name":"A-10.0.0.0_24","type":"ipmask","subnet":"10.0.0.0 255.255.255.0","comment":"demo"}'

# Create ipmask (no JSON)
create-address-ipmask --name "A-10.0.0.0_24" --cidr 10.0.0.0/24

# Update (JSON)
update-address --name "BAN-77.90.151.5" --data '{"comment":"updated"}'

# Update comment (no JSON)
update-address-comment --name "BAN-77.90.151.5" --comment "updated"

# Delete
delete-address --name "*.microsoft.com.akadns.net"
```

> Address creation auto-converts `subnet` between `"IP MASK"` and `["IP","MASK"]` to bypass `500 -5`.

------

### 3) Address Groups

```
# List
list-addrgrps

# Search by substring
search-addrgrps --q "Black"

# Get one (shows members & count)
get-addrgrp --name "Blacklist"

# Create (validate members by default)
create-addrgrp --name "HQ-NETWORKS" --members "A1,A2,A3" --comment "demo"

# Replace fields/members (full replacement)
update-addrgrp --name "HQ-NETWORKS" --members "A-10.0.0.0_24,Another-Addr" --comment "updated"

# Rename
update-addrgrp --name "HQ-NETWORKS" --new-name "HQ-NETWORKS-NEW"

# Add members (idempotent)
add-to-addrgrp --name "HQ-NETWORKS" --members "10.1.6.0/23"

# Remove members
remove-from-addrgrp --name "HQ-NETWORKS" --members "10.1.6.0/23"

# Delete
delete-addrgrp --name "HQ-NETWORKS"

# Find groups that contain a given object
find-groups-with-member --name "BAN-131.226.102.110"
```

**Skip member validation** (when you’re sure members exist or are created out of band): add `--skip-validate-members`.

------

### 4) Smart chunking for groups (≤255 members each)

```
# Provide members inline and/or via file (one per line)
smart-fill-addrgrps \
  --base-name "Blacklist" \
  --members "A-10.0.0.0_24,HQ-NETWORKS" \
  --members-file C:\path\ips.txt \
  --chunk-size 255 \
  --comment "auto-chunked"

# Then attach all -N groups to a policy (dst or src)
attach-grps-to-policy --policy-id 263 --base-name "Blacklist" --direction dst
```

The tool:

- reads existing `base` and `base-2/-3/...` groups,
- fills up to `chunk-size`,
- creates new groups as needed,
- skips members already present.

------

### 5) VIPs (Virtual IPs)

> **VIPs belong in `dstaddr`** of policies. They represent “what external users hit”.
>  For DNAT/port-forward scenarios, policy `nat` is usually **disable** (VIP does the translation); use `service` to restrict ports.

#### List / Search / Get

```
list-vips
search-vips --q "openvpn"
get-vip --name "to-internet"
```

#### Create (JSON)

```
# 1:1 static NAT
create-vip --data '{
  "name": "Pub_1.1.1.1_1to1_10.1.1.1",
  "extip": "1.1.1.1",
  "mappedip": [{"range": "10.1.1.1"}],   // can also be "10.1.1.1"
  "extintf": "any",
  "type": "static-nat",
  "comment": "by API"
}'

# Port forward (tcp/udp/sctp)
create-vip --data '{
  "name": "Pub_1.1.1.1_1to1_10.1.1.1",
  "extip": "1.1.1.1_1",
  "mappedip": "10.1.1.1",
  "portforward": "enable",
  "protocol": "tcp",
  "extport": "943",
  "mappedport": "943",
  "extintf": "any",
  "type": "static-nat"
}'
```

#### Create (no JSON)

```
# Static 1:1
create-vip-simple \
  --name "Pub_1.1.1.1_1to1_10.1.1.1" \
  --extip 1.1.1.1 \
  --mappedip 10.1.1.1 \
  --extintf any \
  --comment "by API"

# Port forward
create-vip-portforward \
  --name "Pub_1.1.1.1_943_10.1.1.1_943" \
  --extip 1.1.1.1 \
  --mappedip 10.1.1.1 \
  --protocol tcp \
  --extport 943 \
  --mappedport 943 \
  --extintf any \
  --comment "by API"
```

> `create-vip-simple` is **for 1:1 static NAT** only (no port args).
>  For port forwarding, use `create-vip-portforward` or `update-vip-fields`.

#### Update

```
# JSON
update-vip --name "Pub_..." --data @vip-update.json

# Field-level (no JSON)
update-vip-fields --name "Pub_..." \
  --portforward true \
  --protocol tcp \
  --extport 943 \
  --mappedport 943 \
  --mappedip 10.1.1.1 \
  --extintf any \
  --comment "443 only"
```

#### Delete

```
delete-vip --name "Pub_..."
```

#### Attach VIP to policy (destination)

```
# Add VIP to dstaddr; remove old internal object if present
policy-set-addrs --policy-id 209 --add-dst "Pub_1.1.1.1_943_10.1.1.1_943" --remove-dst "demo"
```

**Version compatibility built in**

- `extip` may be given with `/32` — the tool strips CIDR.
- `mappedip` accepts `"x.x.x.x"`, `["x.x.x.x"]`, or `[{"range":"x.x.x.x"}]` — normalized internally.
- Ports coerced to strings to satisfy both 7.2/7.4 JSON validators.

------

## 🧪 End-to-End Example: Expose OpenVPN on 943

```
# 1) Create VIP (port forward 943 → 10.1.1.1:943)
create-vip-portforward \
  --name "Pub_1.1.1.1_943_10.1.1.1_943" \
  --extip 1.1.1.1 --mappedip 10.1.1.1 \
  --protocol tcp --extport 943 --mappedport 943 --extintf any

# 2) Attach it to policy 209 (dstaddr), drop old target
policy-set-addrs --policy-id 209 \
  --add-dst "Pub_1.1.1.1_943_10.1.1.1_943" \
  --remove-dst "demo"

# 3) Verify
policy-id --policy-id 209
```

------

## 🛠️ Troubleshooting

- **SSL: `CERTIFICATE_VERIFY_FAILED`**
   Put `--insecure` **before** the subcommand:

  ```
  python <SCRIPT>.py --host ... --token ... --vdom test-vdom --insecure list-vips
  ```

  Or import the FortiGate CA into your system trust store.

- **`424` with VDOM**
   Usually wrong/absent VDOM or per-endpoint limitation. The tool auto-retries list calls without VDOM; ensure your `--vdom` is correct (e.g., `test-vdom`).

- **`500 -7` on policy update**
   Mixing `all` with other members is invalid. The tool auto-removes `all` when you add other names.

- **`500 -5` creating addresses**
   Subnet shape mismatch. The tool retries between `"IP MASK"` and `["IP","MASK"]`. Use `create-address-ipmask` to avoid format issues.

- **`500 -3` when mutating policy addrs**
   Typically caused by putting a **VIP** into `srcaddr`. VIPs belong in **dstaddr** only.

- **`-8` creating VIP** (e.g., “Mapped-ip range is not specified”)
   Provide `--mappedip` or correct JSON shape; the tool normalizes but requires an actual value.

- **“unrecognized arguments”**
   Ensure global flags (`--host --token [--vdom] [--insecure]`) come **before** the subcommand.

------

## 🔒 Best Practices

- Treat API tokens like passwords; avoid shell history leaks.
- Prefer **port-forward VIPs** if you only need specific ports; otherwise use 1:1 and restrict by `service`.
- For DNAT policies, keep `nat` **disable** and rely on VIP; use `service` to allow intended ports only.
- Use `--skip-validate-members` only when you’re sure objects exist.

------

## 🔁 Changelog (SemVer)

### **v1.1.0**

- **New**: VIP CRUD/search, simple creators (1:1 & port-forward), field-level updates.
- **Compat**: Normalize `extip`, `mappedip`, `portforward`, and port types across 7.2/7.4.
- **Polish**: Stronger policy update fallback (light PUT → full merge PUT), auto-remove `all` when mixed.
- **UX**: `--version`, clearer SSL error guidance, better “not found” suggestions.

### v1.0.0

- Policies, addresses, address groups CRUD.
- Smart chunking (≤255 per group) and attach-groups-to-policy.

------

## 📦 Files & JSON Payload Examples

**`policy.json`**

```
{
  "name": "Example-Policy",
  "srcintf": [{"name": "any"}],
  "dstintf": [{"name": "any"}],
  "srcaddr": [{"name": "all"}],
  "dstaddr": [{"name": "all"}],
  "service": [{"name": "ALL"}],
  "action": "accept",
  "schedule": "always",
  "status": "enable",
  "logtraffic": "all",
  "comments": "created by API"
}
```

**`vip-update.json`**

```
{
  "portforward": "enable",
  "protocol": "tcp",
  "extport": "443",
  "mappedport": "443",
  "mappedip": [{"range": "10.146.42.239"}],
  "extintf": "any",
  "comment": "443 only"
}
```

------

## 🧭 Roadmap (optional)

- `--cafile <path>` to validate against a custom CA (safer than `--insecure`).
- `--dry-run` to preview changes without applying.
- Retry/backoff knobs and `--timeout` override.
- VIP groups (`vipgrp`) if needed.

------

## 📄 License

Add your preferred license here (e.g., MIT/Apache-2.0). If omitted, assume “all rights reserved”.
