import datetime, fnmatch, os
from pathlib import Path

import requests

from syncweb import str_utils
from syncweb.log_utils import log
from syncweb.syncthing import SyncthingNode


class Syncweb(SyncthingNode):
    def create_folder_id(self, path):
        existing_folders = set(self.folder_stats().keys())

        name = str_utils.basename(path)
        if name not in existing_folders:
            return name

        return str_utils.path_hash(path)

    def cmd_accept(self, device_ids):
        device_count = 0
        for path in device_ids:
            try:
                device_id = str_utils.extract_device_id(path)
                self.add_device(deviceID=device_id)
                device_count += 1
            except ValueError:
                log.error("Invalid Device ID %s", path)

        return device_count

    def cmd_pause(self, device_ids=None):
        if device_ids is None:
            return self.pause()

        device_count = 0
        for path in device_ids:
            try:
                device_id = str_utils.extract_device_id(path)
                self.pause(device_id)
                device_count += 1
            except ValueError:
                log.error("Invalid Device ID %s", path)

        return device_count

    def cmd_resume(self, device_ids=None):
        if device_ids is None:
            return self.resume()

        device_count = 0
        for path in device_ids:
            try:
                device_id = str_utils.extract_device_id(path)
                self.resume(device_id)
                device_count += 1
            except ValueError:
                log.error("Invalid Device ID %s", path)

        return device_count

    def cmd_add(self, urls, decode=True):
        device_count, folder_count = 0, 0
        for url in urls:
            ref = str_utils.parse_syncweb_path(url, decode=decode)
            if ref.device_id:
                self.add_device(deviceID=ref.device_id)
                device_count += 1

            if ref.folder_id:
                default_path = os.path.realpath(".")
                path = os.path.join(default_path, ref.folder_id)
                os.makedirs(path, exist_ok=True)

                folder_id = self.create_folder_id(path)
                if path not in self.folder_roots:
                    self.add_folder(id=folder_id, path=path, type="receiveonly")
                    self.set_ignores(folder_id)
                    folder_count += 1

                if ref.device_id:
                    self.join_folder(ref.folder_id, [ref.device_id])

                if ref.subpath:
                    # TODO: ask to confirm if ref.subpath == "/" ?
                    # or check size first?
                    self.add_ignores(folder_id, [ref.subpath])

            raise

        return device_count, folder_count

    def cmd_init(self, paths):
        folder_count = 0
        for path in paths:
            os.makedirs(path, exist_ok=True)

            folder_id = self.create_folder_id(path)
            self.add_folder(id=folder_id, path=path, type="sendonly")
            self.set_ignores(folder_id)
            folder_count += 1
        return folder_count

    def add_ignores(self, folder_id: str, exclusions: list[str]):
        existing = set(s for s in self.ignores(folder_id)["ignore"] if not s.startswith("// Syncweb-managed"))

        new = set()
        for p in exclusions:
            if p.startswith("//"):
                continue
            if not p.startswith("!/"):
                p = "!/" + p
            new.add(p)

        combined = new.union(existing)
        ordered = (
            ["// Syncweb-managed"]
            + sorted([p for p in combined if p.startswith("!")])
            + sorted([p for p in combined if not p.startswith("!") and p != "*"])
            + ["*"]
        )

        self.set_ignores(folder_id, lines=ordered)

    def device_short2long(self, short):
        matches = [d for d in self.devices_list if d.startswith(short)]
        if len(matches) == 1:
            dev_id = matches[0]
            return dev_id
        return None

    def device_long2name(self, long):
        short = long[:7]

        try:
            name = self.devices_dict[long].get("name")
            if not name or name.lower() in ("syncweb", "syncthing"):
                return short
            return f"{name} ({short})"
        except KeyError:
            return f"{short}-???????"

    def delete_device_peered_folders(self, device_id: str):
        folders = self._get("config/folders")
        if not folders:
            print(f"[{self.name}] No folders in config.")
            return

        target_folders = [f for f in folders if any(d["deviceID"] == device_id for d in f.get("devices", []))]
        if not target_folders:
            print(f"[{self.name}] No folders offered by or linked to {device_id}.")
            return
        for f in target_folders:
            fid = f["id"]
            print(f"[{self.name}] Deleting folder '{fid}' (linked to {device_id})...")
            try:
                self._delete(f"config/folders/{fid}")
            except requests.HTTPError as e:
                print(f"[{self.name}] Failed to delete folder '{fid}': {e}")

    def accept_pending_devices(self):
        pending = self._get("cluster/pending/devices")
        if not pending:
            log.info(f"[%s] No pending devices", self.name)
            return

        existing_devices = self._get("config/devices")
        existing_device_ids = {d["deviceID"] for d in existing_devices}

        for dev_id, info in pending.items():
            if dev_id in existing_device_ids:
                log.info(f"[%s] Device %s already exists!", self.name, dev_id)
                continue

            name = info.get("name", dev_id[:7])
            log.info(f"[%s] Accepting device %s (%s)", self.name, name, dev_id)
            cfg = {
                "deviceID": dev_id,
                "name": name,
                "addresses": info.get("addresses", []),
                "compression": "metadata",
                "introducer": False,
            }
            self._put(f"config/devices/{dev_id}", json=cfg)

    # TODO: break down more composable
    def accept_pending_folders(self, folder_id: str | None = None):
        pending = self._get("cluster/pending/folders")
        if not pending:
            log.info(f"[%s] No pending folders", self.name)
            return
        if folder_id:
            pending = [f for f in pending if f.get("id") == folder_id]
            if not pending:
                log.info(f"[%s] No pending folders matching '%s'", self.name, folder_id)
                return

        existing_folders = self._get("config/folders")
        existing_folder_ids = {f["id"]: f for f in existing_folders}
        pending = [f for f in pending if f.get("id") not in existing_folder_ids]

        for folder in pending:
            fid = folder["id"]
            offered_by = folder.get("offeredBy", {}) or {}
            device_ids = list(offered_by.keys())

            if not device_ids:
                log.info(f"[%s] No devices offering folder '%s'", self.name, fid)
                continue

            if fid in existing_folder_ids:  # folder exists; just add new devices
                self.join_folder(fid, device_ids)
            else:  # folder doesn't exist; create it (with devices)
                log.info(f"[%s] Creating folder '%s'", self.name, fid)
                cfg = {
                    "id": fid,
                    "label": fid,
                    "path": str(self.home_path / fid),
                    "type": "receiveonly",  # TODO: think
                    "devices": [{"deviceID": d} for d in device_ids],
                }
                self._post("config/folders", json=cfg)

    def join_folder(self, folder_id: str, device_ids: list[str]):
        existing_folder = self.folder(folder_id)

        existing_device_ids = {dd["deviceID"] for dd in existing_folder.get("devices", [])}
        new_devices = [{"deviceID": d} for d in device_ids if d not in existing_device_ids]
        if not new_devices:
            log.info(f"[%s] Folder '%s' already available to all requested devices", folder_id, self.name)
            return

        existing_folder["devices"].extend(new_devices)
        log.debug(f"[%s] Patching '%s' with %s new devices", folder_id, self.name, len(new_devices))
        self._patch(f"config/folders/{folder_id}", json=existing_folder)

    def _is_ignored(self, rel_path: Path, patterns: list[str]) -> bool:
        s = str(rel_path)
        for pat in patterns:
            if fnmatch.fnmatch(s, pat):
                return True
            if fnmatch.fnmatch(s + "/", pat):  # match directories
                return True
        return False

    def disk_usage(self) -> list[dict]:
        results = []
        for folder in self._get("config/folders"):
            folder_id = folder["id"]
            folder_path = Path(folder["path"])

            if not folder_path.exists():
                print(f"[{self.name}] Folder '{folder_id}' path not found: {folder_path}")
                continue

            ignore_patterns = self.ignores(folder_id)

            for dirpath, _dirnames, filenames in os.walk(folder_path):
                rel_dir = Path(dirpath).relative_to(folder_path)
                ignored = self._is_ignored(rel_dir, ignore_patterns)

                total_size = 0
                last_mod = 0

                for f in filenames:
                    fpath = Path(dirpath) / f
                    try:
                        stat = fpath.stat()
                    except FileNotFoundError:
                        continue
                    total_size += stat.st_size
                    last_mod = max(last_mod, stat.st_mtime)

                if total_size == 0 and not filenames:
                    continue  # skip empty dirs

                results.append(
                    {
                        "folder": folder_id,
                        "name": str(rel_dir) if rel_dir != Path(".") else ".",
                        "size": total_size,
                        "last_modified": last_mod,
                        "ignored": ignored,
                    }
                )

        return results

    def flatten_files(self, folder_id: str, prefix: str = "", levels: int | None = None):
        def _recurse(entries, path_prefix):
            flat = []
            for e in entries:
                name = e["name"]
                typ = e.get("type")
                full_path = f"{path_prefix}/{name}" if path_prefix else name
                if typ == "FILE_INFO_TYPE_FILE":
                    modtime = datetime.datetime.fromisoformat(e["modTime"])
                    flat.append({"path": full_path, "size": e["size"], "modTime": modtime})
                elif typ == "FILE_INFO_TYPE_DIRECTORY" and "children" in e:
                    flat.extend(_recurse(e["children"], full_path))
            return flat

        tree = self.files(folder_id, prefix=prefix, levels=levels)
        return _recurse(tree, prefix)

    def aggregate_directory(self, folder_id: str, prefix: str = "", levels: int | None = None):
        files = self.flatten_files(folder_id, prefix=prefix, levels=levels)
        if not files:
            return {"total_size": 0, "last_modified": None}

        total_size = sum(f["size"] for f in files)
        last_modified = max(f["modTime"] for f in files)
        return {"total_size": total_size, "last_modified": last_modified}

    def aggregate_files(self, files: list[dict]):
        if not files:
            return {"total_size": 0, "last_modified": None, "count": 0}

        total_size = sum(f["size"] for f in files)
        last_modified = max(f["modTime"] for f in files)
        count = len(files)
        return {"total_size": total_size, "last_modified": last_modified, "count": count}
