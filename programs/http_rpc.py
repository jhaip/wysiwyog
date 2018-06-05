import RPCClient
from flask import Flask, jsonify, abort

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        params = request.get_json()
        event = params.get("event")
        options = params.get("options")
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
        event = request.args.get("event")
        options = request.args.get("options")
        if event == "get_wishes_by_type":
            d = M.get_wishes_by_type(options.get("type"))
            return jsonify(d)
        elif event == "when":
            d = M.stop_program(options.get("source"), options.get("key"))
            return jsonify(d)
        elif event == "get_image":
            abort(400)
        abort(404)
