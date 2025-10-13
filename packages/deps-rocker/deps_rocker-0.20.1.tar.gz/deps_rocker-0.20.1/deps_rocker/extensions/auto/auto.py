"""Automatically detect and enable extensions based on workspace files"""

from rocker.extensions import RockerExtension
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed  # pylint: disable=E0611


class Auto(RockerExtension):
    def _resolve_workspace(self, cliargs):
        root = cliargs.get("auto")
        # If root is True (from --auto with no value), treat as None
        if root is True or root is None or not isinstance(root, (str, Path)):
            path = Path.cwd().expanduser().resolve()
        else:
            path = Path(root).expanduser().resolve()
        print(f"[auto-detect] Scanning workspace: {path}")
        print(f"[auto-detect] Workspace exists: {path.exists()}")
        print(f"[auto-detect] Workspace is_dir: {path.is_dir()}")
        return path

    # Detect project files and enable relevant extensions based on workspace contents.
    # Use --auto=~/renv to specify the root directory for recursive search.

    @classmethod
    def get_name(cls):
        return cls.name

    @staticmethod
    def register_arguments(parser, defaults=None):
        """
        Register command-line arguments for the auto extension.
        """
        parser.add_argument(
            "--auto",
            type=str,
            nargs="?",
            const=str(Path.cwd()),
            help="Enable auto extension and optionally specify a search root directory. Defaults to current working directory.",
        )

    name = "auto"

    def _detect_files_in_workspace(self, _cliargs: dict) -> set[str]:
        """
        Detect files in the workspace and return a set of extension names to enable, in parallel.
        """
        import yaml

        workspace = self._resolve_workspace(_cliargs)

        extensions_dir = Path(__file__).parent.parent
        file_patterns = {}
        dir_patterns = {}
        for ext_dir in extensions_dir.iterdir():
            if not ext_dir.is_dir():
                continue
            rule_file = ext_dir / "auto_detect.yml"
            if rule_file.exists():
                with rule_file.open() as f:
                    rules = yaml.safe_load(f)
                ext_name = ext_dir.name
                # File patterns
                for fname in rules.get("files", []):
                    file_patterns[fname] = ext_name
                # Directory patterns
                for dname in rules.get("config_dirs", []):
                    dir_patterns[dname] = ext_name

        # Prepare detection functions and their arguments
        # Use only patterns from auto_detect.yml files for all extensions
        tasks = [
            (self._detect_exact_dir, (workspace, dir_patterns)),
            (self._detect_glob_patterns, (workspace, file_patterns)),
        ]

        results = set()
        print("[auto-detect] Running detection tasks in parallel...")
        with ThreadPoolExecutor() as executor:
            future_to_task = {executor.submit(func, *args): func.__name__ for func, args in tasks}
            for future in as_completed(future_to_task):
                task_name = future_to_task[future]
                try:
                    res = future.result()
                    print(f"[auto-detect] {task_name} detected: {res}")
                    results |= res
                except Exception as e:
                    print(f"[auto-detect] {task_name} failed: {e}")

        print(f"[auto-detect] Final detected extensions: {results}")
        return results

    def _detect_glob_patterns(self, workspace, file_patterns):
        import time
        import os
        import fnmatch

        found = set()
        start_total = time.time()
        # Walk the tree once, handling symlinks and permission errors
        all_files = []
        workspace_path = str(workspace)
        walk_errors = []

        def walk_onerror(err):
            walk_errors.append(err)

        for root, dirs, files in os.walk(workspace_path, onerror=walk_onerror, followlinks=False):
            # Remove symlinked directories from dirs to prevent walking them
            dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(root, d))]
            for fname in files:
                fpath = os.path.join(root, fname)
                # Skip symlinked files
                if os.path.islink(fpath):
                    continue
                try:
                    relpath = os.path.relpath(fpath, workspace_path)
                    all_files.append(relpath)
                except Exception as e:
                    walk_errors.append(e)
        # Match patterns in memory
        for pattern, ext in file_patterns.items():
            start = time.time()
            matches = [f for f in all_files if fnmatch.fnmatch(f, pattern)]
            duration = time.time() - start
            if matches:
                print(
                    f"[auto-detect] ✓ Detected {pattern} ({len(matches)} matches) -> enabling {ext} [search took {duration:.3f}s]"
                )
                found.add(ext)
            else:
                print(
                    f"[auto-detect] Pattern {pattern} found no matches [search took {duration:.3f}s]"
                )
        print(f"[auto-detect] Total file walk and match time: {time.time() - start_total:.3f}s")
        return found

    def _detect_exact_dir(self, workspace, patterns):
        found = set()
        # Check in workspace
        for dname, ext in patterns.items():
            dir_path = workspace / dname
            if dir_path.is_dir():
                print(f"[auto-detect] ✓ Detected {dname} directory in workspace -> enabling {ext}")
                found.add(ext)
        # Check in user's home directory
        home = Path.home()
        for dname, ext in patterns.items():
            dir_path = home / dname
            if dir_path.is_dir():
                print(f"[auto-detect] ✓ Detected {dname} directory in home -> enabling {ext}")
                found.add(ext)
        return found

    def required(self, cliargs: dict) -> set[str]:
        """
        Returns a set of dependencies required by this extension based on detected files.

        Args:
            cliargs: CLI arguments dict

        Returns:
            Set of extension names to enable
        """
        return self._detect_files_in_workspace(cliargs)
