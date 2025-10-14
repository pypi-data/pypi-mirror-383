#!/usr/bin/env python3

import hashlib
from pathlib import Path

# compute sha for repo.7z file in current directory
# use this if you want to convert a file from a previous verison of git-remote-rclone to the
# current version. Compute its hash with this script, and then rename it like so:
#
# mv repo.7z repo-<SHA>.7z
# 
# Then, uncompress repo-<SHA>.7z and recompress with tar, so you have repo-<SHA>.tar.gz:
# 7z e repo-<SHA>.7z
# tar -czf repo-<SHA>.tar.gz repo

repo_file = Path("repo.7z")
repo_hash = hashlib.sha1(repo_file.read_bytes()).hexdigest()
print(repo_hash)
