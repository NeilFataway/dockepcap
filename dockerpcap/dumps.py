# coding=utf-8

import os
import signal
import pickle
import subprocess
import config
import utils
import psutil
import shutil
import time
from datetime import datetime
from threading import Thread
import docker, docker.errors
import errors


# initialize docker client
DClient = docker.from_env()


# register signal handler to prevent from zombie process
def signal_chld_handler(signum_, frame):
    try:
        while not os.waitpid(-1, os.WNOHANG):
            return
    except OSError:
        pass


signal.signal(signal.SIGCHLD, signal_chld_handler)
signal.siginterrupt(signal.SIGCHLD, False)


class Dump(object):
    def __init__(self, container_id, net_filter=None):
        self.id = utils.generate_uuid()
        self.container_id = container_id
        self.created_at = datetime.now()
        self.work_dir = os.path.join(config.BASE_WORK_DIR, self.id)
        if net_filter:
            cmd = ["ddump", "-f", net_filter, "--max-duration", str(int(config.MAX_DUMP_DURATION.total_seconds())),
                   "--max-filesize", str(int(config.MAX_DUMP_SIZE)), self.work_dir, self.net_ns_path]
        else:
            cmd = ["ddump", "--max-duration", str(int(config.MAX_DUMP_DURATION.total_seconds())),
                   "--max-filesize", str(int(config.MAX_DUMP_SIZE)), self.work_dir, self.net_ns_path]
        if not os.path.isdir(self.work_dir):
            os.makedirs(self.work_dir)
        process = subprocess.Popen(cmd, cwd=self.work_dir)
        self.pid = process.pid
        self.write_metadata()

    @property
    def net_ns_path(self):
        try:
            container = DClient.containers.get(self.container_id)
            if container.attrs.get("HostConfig", {}).get("NetworkMode").startswith("container:"):
                pod_container_id = container.attrs.get("HostConfig", {}).get("NetworkMode").split(":")[1].strip()
                pod_container = DClient.containers.get(pod_container_id)
                ns_path = pod_container.attrs.get("NetworkSettings", {}).get("SandboxKey")
            else:
                ns_path = container.attrs.get("NetworkSettings", {}).get("SandboxKey")

            return ns_path
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
    def expired_at(self):
        return self.created_at + config.EXPIRED_DURATION


    @property
    def is_running(self):
        try:
            return psutil.Process(pid=self.pid).is_running()
        except psutil.NoSuchProcess:
            return False

    def terminate(self):
        try:
            psutil.Process(pid=self.pid).terminate()
        except psutil.NoSuchProcess:
            pass

    def wait(self):
        try:
            psutil.Process(pid=self.pid).wait()
        except psutil.NoSuchProcess:
            pass

    def expire(self):
        if os.path.isdir(self.work_dir):
            shutil.rmtree(self.work_dir)

    def write_metadata(self):
        with open(os.path.join(self.work_dir, "metadata"), "w") as f:
            return pickle.dump(self, f)

    @staticmethod
    def load(dump_id):
        try:
            with open(os.path.join(config.BASE_WORK_DIR, dump_id, "metadata")) as f:
                return pickle.load(f)
        except IOError:
            raise errors.DumpNotFoundError

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


class DumpManager(dict, Thread):
    def __init__(self, interval):
        self.interval = interval
        dict.__init__(self)
        Thread.__init__(self)
        if os.path.isdir(config.BASE_WORK_DIR):
            for dump_id in os.listdir(config.BASE_WORK_DIR):
                self[dump_id] = Dump.load(dump_id)

    def run(self):
        while True:
            now = datetime.now()
            for dump in self.itervalues():
                if dump.expired_at <= now:
                    dump.expire()
            time.sleep(self.interval)

    def __getitem__(self, dump_id):
        try:
            return dict.__getitem__(self, dump_id)
        except KeyError:
            dump = Dump.load(dump_id)
            self[dump_id] = dump
            return dump

    def __hash__(self):
        return id(self)
