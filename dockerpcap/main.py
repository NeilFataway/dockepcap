# coding=utf-8
from flask import Flask, request, Response, jsonify
from dumps import Dump, DumpManager
import errors
import config
import os


app = Flask(__name__)
dump_manager = DumpManager(config.CRON_INTERVAL.total_seconds())
dump_manager.start()
errors.setup_exception(app)


@app.route("/dumps/create", methods=["POST"])
def dump_create():
    container_id = request.json.get("container_id")
    if not container_id:
        raise errors.InvalidUsage("container_id not specified.")
    net_filter = request.json.get("net_filter")
    dump = Dump(container_id, net_filter)
    dump_manager[dump.id] = dump
    return dump.json


@app.route("/dumps/<dump_id>/stop", methods=["POST"])
def dump_stop(dump_id):
    dump = dump_manager[dump_id]
    dump.terminate()
    dump.wait()
    return dump.json


@app.route("/dumps/<dump_id>/stop_and_download", methods=["POST"])
def dump_stop_and_download(dump_id):
    dump = dump_manager[dump_id]
    dump.terminate()
    dump.wait()
    response = Response(dump.send_file(), content_type='application/octet-stream')
    response.headers.set("Content-Disposition", "attachment; filename={}.{}".format(dump_id, "pcap"))
    return response


@app.route("/dumps/<dump_id>/download", methods=["GET"])
def dump_download(dump_id):
    dump = dump_manager[dump_id]
    if dump.is_running:
        raise errors.ResourceLocked("dump process still running, download locked.")
    response = Response(dump.send_file(), content_type='application/octet-stream')
    response.headers.set("Content-Disposition", "attachment; filename={}.{}".format(dump_id, "pcap"))
    return response


@app.route("/dumps/<dump_id>/detail", methods=["GET"])
def dump_detail(dump_id):
    dump = dump_manager[dump_id]
    return dump.json


@app.route("/dumps/list", methods=["GET"])
def dump_list():
    if not os.path.isdir(config.BASE_WORK_DIR):
        return jsonify([])
    else:
        return jsonify(os.listdir(config.BASE_WORK_DIR))


def main():
    app.run(host="0.0.0.0", port=config.HTTP_PORT, debug=True)
