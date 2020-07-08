from flask import Flask, render_template, redirect, session, request, jsonify, make_response
from engine import *

#TODO/MAYBE: ADD game/session reset
#TODO/MAYBE: Remove displayed stone when courser moves out of the board/canvas.
#DONE: Add Komi Options and show/store them.
#DONE: Add game end & counting.
#DONE: Add Komi  & scoring functionality
#DONE: Ko Check does not work??
#DONE: Make last_stone dissapear when hovering over a permanent stone.
#DONE: Fix that a player can remove his last liberty without the group getting removed.
#DONE: Add pass option
#DONE: Solve placement should check the current group after checking the neighbors.
#DONE: Add captures & current player display

app = Flask(__name__)
#need to set secret key to work with sessions
app.secret_key = "Apfelwein"

@app.route('/', methods=["GET", "POST"])
def setup_page():
	if request.method == "GET":
		return render_template("index.html")
	elif request.method == "POST":
		size = int(request.form.get("boardSize"))
		session["board_size"] = size
		session["komi"] = float(request.form.get("komi"))
		return redirect("/game")


@app.route('/game')
#maybe try adding a size_required decorator later
def game():
	return render_template("game.html")

#get called/fetched from /game at opening the page to get board size.
@app.route('/setup', methods=["GET"])
def setup():
	session["moves"] = []
	session["state"] = [[None for i in range(session["board_size"])] for i in range(session["board_size"])]
	session["changes"] = []
	session["cap_black"] = 0
	session["cap_white"] = 0
	session["move_nr"] = len(session["moves"]) + 1
	session["removing"] = False
	session["end"] = False
	res = make_response(jsonify(
						{"size": session["board_size"],
						"state": session["state"],
						"changes": session["changes"],
						"current_color": True,
						"move_nr": len(session["moves"]) +1,
						"komi": session["komi"]
						}), 200)
	return res

@app.route('/update', methods=["POST"])
#maybe size_required decorator
def update():
	r = request.get_json()
	new_move = r.get("coords")
	e = Engine(session.get("board_size"))
	#returns T/F for valid/invalid moves and saves changes in self.changes
	if e.app_updater(session["moves"], new_move):
		#basically not needed,,,, well yea needed.
		#app updater should use a temp moves list in case in case the move in invalid.
		board_changes = e.changes[-1]
		session["current_color"] = e.current_player #T = black, F = white
		session["state"] = e.curr_board_state
		session["cap_black"] = e.points.get("black")
		session["cap_white"] = e.points.get("white")
		session["removing"] = e.removing
		session["end"] = e.end
		if session["end"]:
			#must return response immediatly
			pt_black = e.points["black"]
			pt_white = e.points["white"] + session["komi"]
			if pt_black > pt_white:
				winner = True
			else:
				winner = False

			res = jsonify({ "end": session["end"], "winner": winner,
							"pt_black": pt_black, "pt_white": pt_white})
			return res

		if not e.removing:
			session["move_nr"] = len(session["moves"]) +1

		res = jsonify({"board_changes": board_changes,
						"board_state": session["state"],
						"current_color": session["current_color"],
						"cap_black": session["cap_black"],
						"cap_white": session["cap_white"],
						"move_nr": session["move_nr"],
						"removing": session["removing"],
						"end": session["end"]})
	else:
		#move was invalid
		res = jsonify({"board_changes": None, "board_state": session["state"], "current_color": session["current_color"],
		"cap_black": session["cap_black"], "cap_white": session["cap_white"], "move_nr": session["move_nr"]})
	return res


if __name__ == '__main__':
	app.run(host='0.0.0.0')
