import os
import yaml
import subprocess

def findpath(dirs, path):
    if len(dirs) == 0:
        return path

    for directory in dirs:
        joined = os.path.join(directory, path)
        if os.path.exists(joined):
            return joined
    raise KeyError, "Can't find '{0}' in {1}".format(path, dirs)

def which(name):
    paths = os.getenv('PATH')
    for path in paths.split(os.path.pathsep):
        exe = os.path.join(path, name)
        if os.path.exists(exe) and os.access(exe, os.F_OK|os.X_OK):
            return exe
    raise KeyError, "Can't find '{0}' in PATH".format(name)

def checkpoint(workdir, key):
    statusfile = os.path.join(workdir, 'status.yaml')
    if os.path.exists(statusfile):
        with open(statusfile, 'rb') as f:
            s = yaml.load(f)
            return s.get(key)
    else:
        return False

def register_checkpoint(workdir, key, value):
    statusfile = os.path.join(workdir, 'status.yaml')
    with open(statusfile, 'a') as f:
        yaml.dump({key: value}, f, default_flow_style=False)

def ldd(name):
    libs = []

    env = dict(os.environ)

    def anti_cms_filter(d):
        return not (d.startswith('/cvmfs') or 'grid' in d or 'cms' in d)

    env["LD_LIBRARY_PATH"] = os.path.pathsep.join(
            filter(anti_cms_filter, os.environ.get("LD_LIBRARY_PATH", "").split(os.path.pathsep)))
    env["PATH"] = os.path.pathsep.join(
            filter(anti_cms_filter, os.environ.get("PATH", "").split(os.path.pathsep)))

    p = subprocess.Popen(["ldd", which(name)], env=env,
            stdout=subprocess.PIPE)
    out, err = p.communicate()

    for line in out.splitlines():
        fields = line.split()

        if len(fields) < 3 or fields[1] != "=>":
            continue

        lib = fields[0]
        target = fields[2]

        if lib.startswith('libssl') or lib.startswith('libcrypto'):
            libs.append(target)

    return libs
