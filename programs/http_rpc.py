import RPCClient
from flask import Flask, jsonify, abort

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
M = RPCClient.RPCClient()

id = sys.argv[1]

@app.route('/', methods=['GET', 'POST'])
def hello():
    params = request.get_json()
    event = params.get("event")
    if request.method == 'POST':
        if event == "clear_wishes":
            d = M.clear_wishes(params.get("opts"))
            return jsonify(d)
        elif event == "wish":
            d = M.wish(params.get("type"), params.get("source"), params.get("action"))
            return jsonify(d)
        elif event == "claim":
            d = M.claim(params.get("source"), params.get("key"), params.get("value"))
            return jsonify(d)
        elif event == "stop_program":
            d = M.stop_program(params.get("id"))
            return jsonify(d)
        elif event == "run_program":
            d = M.run_program(params.get("id"), params.get("restart", False))
            return jsonify(d)
        elif event == "create_program":
            d = M.create_program(params.get("name"))
            return jsonify(d)
        elif event == "update_program":
            d = M.update_program(params.get("program_id"), params.get("new_code"))
            return jsonify(d)
        abort(404)
    else:
        if event == "get_wishes_by_type":
            d = M.get_wishes_by_type(params.get("type"))
            return jsonify(d)
        elif event == "when":
            d = M.stop_program(params.get("source"), params.get("key"))
            return jsonify(d)
        elif event == "get_image":
            abort(400)
        abort(404)
