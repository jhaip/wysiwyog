import sys
import RPCClient
import logging
import json
from flask import Flask, jsonify, abort, request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

@app.route('/', methods=['GET', 'POST'])
def hello():
    logging.info("request!")
    if request.method == 'POST':
        params = request.get_json()
        event = params.get("event")
        options = params.get("options")
        logging.info("RECEIVED POST REQUEST")
        logging.info(params)
        if event == "clear_wishes":
            d = M.clear_wishes(options.get("opts"))
            return jsonify(d)
        elif event == "wish":
            d = M.wish(options.get("type"), options.get("source"), options.get("action"))
            return jsonify(d)
        elif event == "claim":
            d = M.claim(options.get("source"), options.get("key"), options.get("value"))
            return jsonify(d)
        elif event == "stop_program":
            d = M.stop_program(options.get("id"))
            return jsonify(d)
        elif event == "run_program":
            d = M.run_program(options.get("id"), options.get("restart", False))
            return jsonify(d)
        elif event == "create_program":
            d = M.create_program(options.get("name"))
            return jsonify(d)
        elif event == "update_program":
            d = M.update_program(options.get("program_id"), options.get("new_code"))
            return jsonify(d)
        abort(404)
    else:
        logging.info("RECEIVED GET REQUEST")
        logging.info(request.args)
        is_test = request.args.get("test")
        if is_test:
            return jsonify({"hello": "world"})
        event = request.args.get("event")
        options = request.args.get("options")
        if options:
            options = json.loads(options)

        if event == "get_wishes_by_type":
            d = M.get_wishes_by_type(options.get("type"))
            return jsonify(d)
        elif event == "when":
            d = M.when_no_callback(options.get("source"), options.get("key"))
            return jsonify(d)
        elif event == "get_image":
            abort(400)
        abort(404)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
