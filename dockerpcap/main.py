# coding=utf-8
from flask import Flask, request, Response, jsonify
from dumps import Dump
import errors
import config
import os


app = Flask(__name__)
errors.setup_exception(app)
jobs = {}


@app.route("/dumps/create", method=["POST"])
def dump_create():
    container_id = request.json.get("container_id")
    if not container_id:
        raise errors.InvalidUsage("container_id not specified.")
    dump = Dump(container_id)
    return dump.json


@app.route("/dumps/{dump_id}/stop")
def dump_stop(dump_id):
    dump = Dump.load(dump_id)
    dump.terminate()
    dump.wait()
    return dump.json


@app.route("/dumps/{dump_id}/stop_and_download")
def dump_stop(dump_id):
    dump = Dump.load(dump_id)
    dump.terminate()
    dump.wait()
    return Response(dump.send_file(), content_type='application/octet-stream')


@app.route("/dumps/{dump_id}/download")
def dump_stop(dump_id):
    dump = Dump.load(dump_id)
    if dump.is_runnning():
        raise errors.ResourceLocked("dump process still running, download locked.")
    return Response(dump.send_file(), content_type='application/octet-stream')


@app.route("/dumps/{dump_id}/detail")
def dump_stop(dump_id):
    dump = Dump.load(dump_id)
    return dump.json


@app.route("/dumps/list")
def dump_list():
    if not os.path.isdir(config.BASE_WORK_DIR):
        return jsonify([])
    else:
        return jsonify(os.listdir(config.BASE_WORK_DIR))


def main():
    app.run(port=80, debug=True)
