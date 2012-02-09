#!/usr/bin/env python

import sys, os
import hashlib
import stat

if len(sys.argv) < 1:
    print("Error, rpm command not specified")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Error, no paths specified")
    sys.exit(1)

paths = sys.argv[2:]

for path in paths:
    if os.path.exists(path + "/solvedb.done"):
        continue
    data = ""
    manifest = []
    for root, dirs, files in os.walk(path):
        for file in files:
            f = os.path.join(root, file)
            if f.startswith(path + "/" + "solvedb"):
                continue
            data = data + str(os.stat(f)[stat.ST_MTIME])
            manifest.append(f)
    checksum = hashlib.md5(data).hexdigest()

    if os.path.exists(path + "/solvedb.checksum") and open(path + "/solvedb.checksum", "r").read() == checksum:
        open(path + "/solvedb.done", "w")
        continue

    if not os.path.exists(path + "/solvedb"):
        os.mkdir(path + "/solvedb")
    m = open(path + "/solvedb/manifest", "w")
    m.write("# Dynamically generated solve manifest\n")
    for f in manifest:
        m.write(f + "\n")
    m.close()

    cmd = sys.argv[1] + ' -i --replacepkgs --replacefiles --oldpackage -D "_dbpath ' + path + '/solvedb" --justdb \
			--noaid --nodeps --noorder --noscripts --notriggers --noparentdirs --nolinktos --stats \
			--ignoresize --nosignature --nodigest -D "__dbi_txn create nofsync" \
			' + path + '/solvedb/manifest'
    os.system(cmd)

    open(path + "/solvedb.checksum", "w").write(checksum)
    open(path + "/solvedb.done", "w")

