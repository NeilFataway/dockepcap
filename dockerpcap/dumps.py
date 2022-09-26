# coding=utf-8

import os
import signal
import pickle
import subprocess
import config
import utils
import psutil
import shutil
from datetime import datetime
import docker, docker.errors
import errors


# initialize docker client
DClient = docker.from_env()


# register signal handler to prevent from zombie process
def signal_chld_handler(signum_, frame):
    while not os.waitpid(-1, os.WNOHANG):
        return


signal.signal(signal.SIGCHLD, signal_chld_handler)
signal.siginterrupt(signal.SIGCHLD, False)


class Dump(object):
    def __init__(self, container_id, net_filter=None):
        self.id = utils.generate_uuid()
        self.container_id = container_id
        self.created_at = datetime.now()
        self.expired_at = self.created_at + config.EXPIRED_DURATION
        self.work_dir = os.path.join(config.BASE_WORK_DIR, self.id)
        if not os.path.isdir(self.work_dir):
            os.makedirs(self.work_dir)
        if net_filter:
            cmd = ["ddump", "-f", net_filter, "--max-duration", int(config.MAX_DUMP_DURATION.total_seconds()),
                        "--max-filesize", int(config.MAX_DUMP_SIZE), self.work_dir, self.net_ns_path]
        else:
            cmd = ["ddump", "--max-duration", int(config.MAX_DUMP_DURATION.total_seconds()),
                        "--max-filesize", int(config.MAX_DUMP_SIZE), self.work_dir, self.net_ns_path]
        process = subprocess.Popen(cmd, cwd=self.work_dir)
        self.pid = process.pid
        self.write_metadata()

    @property
    def net_ns_path(self):
        try:
            return DClient.containers.get(self.container_id).attrs.get("NetworkSettings", {}).get("SandboxKey")
        except docker.errors.NotFound:
            raise errors.ContainerNotFoundError

    @property
    def dump_file_size(self):
        data_file = os.path.join(self.work_dir, "data.pcap")
        if os.path.exists(data_file):
            st = os.stat(data_file)
            return st.st_size
        else:
            return 0

    @property
    def is_running(self):
        return psutil.Process(pid=self.pid).is_running()

    def terminate(self):
        psutil.Process(pid=self.pid).terminate()

    def wait(self):
        psutil.Process(pid=self.pid).wait()

    def __del__(self):
        if self.work_dir:
            shutil.rmtree(self.work_dir)

    def write_metadata(self):
        with open(os.path.join(self.work_dir, "metadata"), "w") as f:
            return pickle.dump(self, f)

    @staticmethod
    def load(dump_id):
        with open(os.path.join(config.BASE_WORK_DIR, dump_id, "metadata")) as f:
            return pickle.load(f)

    @property
    def json(self):
        return {
            "id": self.id,
            "container_id": self.container_id,
            "is_running": self.is_running,
            "created_at": self.created_at.ctime(),
            "expired_at": self.expired_at.ctime(),
            "dump_file_size": self.dump_file_size
        }

    def send_file(self):
        with open(os.path.join(self.work_dir, "data.pcap")) as f:
            while True:
                data = f.read(config.BUFF_SIZE)
                if len(data) == 0:
                    break
                else:
                    yield data
        return
