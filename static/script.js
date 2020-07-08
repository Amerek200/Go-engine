//still need to clear up when/where/how and WHY the declaration of each variable makes sense.
var canvas;
var ctx;
var width;
var height;
var board_size;
var outer_margin;
var inner_margin;
var stone_size;
//last_stone to keep track and remove temporary "painted" stones while moving over the board with the courser.
var last_stone = [undefined, undefined];
var max_value;
var pass_button;
var cap_white;
var cap_black;
var color;
var curr_color;
var move_nr;
var removing = false;
var end = false;
var komi;
var state;


window.onload = function () {
    canvas = document.getElementById("game");
    pass_button = document.getElementById("pass_button");
    cap_white = document.getElementById("cap_white");
    cap_black = document.getElementById("cap_black");
    curr_color = document.getElementById("curr_color");
    move_nr = document.getElementById("move_nr");
    ctx = canvas.getContext("2d");
    width = canvas.width;
    height = canvas.height;

    //fetch board size and call setup, specifying method not needed, GET is default.
    fetch("/setup", {method: "GET"})
      .then(function (response) {
        if (response.status !== 200) {
          console.log(`Error, Status code: ${response.status}`); // `` used for template strings instead of " or '.
          return;
        }
        response.json().then(function (data) {
            setup(data);
        })
      })
    //https://www.w3schools.com/jsref/event_preventdefault.asp
    //or return false ->prevents reloading after submitting
    //size_form.onsubmit = function() {setup(); return false;};
};

function setup(data) {
    //board_size = document.querySelector("#boardSize").value;
    board_size = data.size;
    var changes = data.changes;
    state = data.state;
    color = data.current_color;
    document.getElementById("komi").innerHTML = data.komi;
    draw_board();

    canvas.addEventListener("mousemove", function(evt) {
        var pos = get_mouse_coord(canvas, evt);
        //turns -0 in 0 and moves under/over board range into false.
        var x = clean_coord_value(pos.x);
        var y = clean_coord_value(pos.y);
        //haha, javascript evaluates 0 to false, check for same type as well -> works.
        if ((x !== false) && (y !== false) && state[x][y] == null && removing == false) {
            app_display_stone([x, y], color);
        }
        else if ((x !== false) && (y !== false) && state[x][y] != null) {
            //correct coords but there is already a stone -> we have to clear last pos.
            clear_pos(last_stone);
        }
    });

    canvas.addEventListener("click", function(evt) {
        game_click_handler(evt);
    });
    pass_button.addEventListener("click", send_pass);
}


function game_click_handler(evt) {
    //called at setup, removed when data.removing = True I guess.
    var pos = get_mouse_coord(canvas, evt);
    var x = clean_coord_value(pos.x);
    var y = clean_coord_value(pos.y);

    if (x !== false && y !== false && (state[x][y] == null || (removing == true && state[x][y] !== null))) {
        var coords = [x, y];
        fetch('/update',
            {method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({"coords": coords})
            })
        .then(function (response) {
            if (response.status !== 200) {
                console.log(`Error, Status code: ${response.status}`); // `` used for template strings instead of " or '.
                return;
            }
            //.json() returns a promise object (used for .then chaining) and should be used with fetch.
            //JSON.parse() returns a javascript object.
            response.json().then(function (data) {
                if (data.board_changes != null) {
                    apply_changes(data.board_changes);
                }
                state = data.board_state;
                color = data.current_color;
                update_captures(data.cap_black, data.cap_white);
                update_header(data.move_nr, color, data.removing);
            });
        });
    }
}


function send_pass() {
    //sends coord = pass to server on button click.
    fetch('/update',
        {method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"coords": "pass"})
        })
    .then(function (response){
        if (response.status !== 200) {
            console.log(`Error, status code: ${response.status}`);
            return;
        }
        response.json().then(function (data) {
            if (data.end == true) {
                final_header(data.winner, data.pt_black, data.pt_white);
            } else {
                state = data.board_state;
                color = data.current_color;
                removing = data.removing;
                update_header(data.move_nr, color, removing);
            }
        });
    });
}

function update_captures(black, white) {
    cap_black.innerHTML = black;
    cap_white.innerHTML = white;
}

function update_header(move, color, rem) {
    if (rem == true) {
        console.log("entering rem = true loop")
        document.getElementById("move_header").innerHTML = "<h3>Click on dead stones to remove the group. <br> Click Pass to continue to counting.</h3>";
    } else {
        move_nr.innerHTML = move;
        if (color == true) {
            curr_color.innerHTML = "Black";
        }
        else {
            curr_color.innerHTML = "White";
        }
    }
}

function final_header(winner, pt_black, pt_white) {
    if (winner == true) {
        document.getElementById("move_header").innerHTML = `Black wins with ${pt_black} to ${pt_white} points`;
    } else {
        document.getElementById("move_header").innerHTML = `White wins with ${pt_white} to ${pt_black} points`;
    }
}

function apply_changes(changes) {
    changes.forEach(function(item) {
        var pos = item.slice(0, 2);
        //kind of doubled to check here for color == T/F, but otherwise I would get a ptoblem with the null/deletion?
        if (item[2] == true) {
            //True, meaning white
            draw_stone(pos, true);
            //clear last stone to prevent "displayfromapp" from clearing is immediatly.
            last_stone = [undefined, undefined];
        }
        else if (item[2] == false) {
            draw_stone(pos, false);
            last_stone = [undefined, undefined];
        }
        else {
            //must be null
            clear_pos(pos);
        }
    })
}

//draws a single stone on a give coordinate.
//position = array [x, y]
function draw_stone(pos, color) {
    let x = outer_margin + pos[0] * inner_margin;
    let y = outer_margin + pos[1] * inner_margin;
    ctx.beginPath();
    ctx.arc(x, y, stone_size, 0, 2*Math.PI)
    if (color == true){
        ctx.fillStyle = "black";
    }
    else {
        ctx.fillStyle = "white";
    }
    ctx.closePath();
    ctx.fill();
}

function get_mouse_coord(canvas, evt) {
	var canv_pos = canvas.getBoundingClientRect();
	//get courser x,y pos with 0,0 board point == 0,0 pos.
	var x = evt.clientX - canv_pos.left - outer_margin;
	var y = evt.clientY - canv_pos.top - outer_margin;

	x = Math.round(x * ((board_size -1) / (width - 2 * outer_margin)));
	y = Math.round(y * ((board_size -1) / (height - 2 * outer_margin)));
	return { "x": x , "y": y};
}

function clean_coord_value(x) {
    //clean values from -0 to 0,
    //remove -1 and board_size+1 -> return false
    if (x == -0) {
        return 0;
    }
    else if ((x < 0) || (x > board_size-1)) {
        return false;
    }
    else {
        return x;
    }
}

function app_display_stone(coords, current_color) {
	var x = coords[0];
	var y = coords[1];
	//create last and current stone variable to keep track and remove a stone when it's not hovered above.
	var current_stone;
	//filter out negativ or to big board coords: (check if I can use cleanCoord?)
	if ((0 <= x && x < board_size) && (0 <= y && y < board_size)) {
		draw_stone([x, y], current_color);
		current_stone = [x, y]
		//cant directly compare arrays in javascript, need to check every element
		if (identical_pos(current_stone, last_stone) == false) {
			clear_pos(last_stone);
			last_stone = current_stone ;
		}
	}
}

function clear_pos(coords){
	//would it be easier/faster to compute with just fillrect? seems better then the size +1 thing,,
	let x = outer_margin + coords[0] * inner_margin;
	let y = outer_margin + coords[1] * inner_margin;
	ctx.beginPath();
	ctx.arc(x, y, stone_size + 1, 0, 2*Math.PI);
	ctx.fillStyle = "#ac7339";
	ctx.closePath();
	ctx.fill();
	ctx.beginPath();
	ctx.moveTo(clean_value(x - (inner_margin * 0.51)), clean_value(y));
	ctx.lineTo(clean_value(x + (inner_margin * 0.51)), clean_value(y));
	ctx.moveTo(clean_value(x), clean_value((y - inner_margin * 0.51)));
	ctx.lineTo(clean_value(x), clean_value((y + inner_margin * 0.51)));
	ctx.closePath();
	ctx.stroke();
}

function identical_pos(a, b){
	//checks if two coord arrays are identical for mousemove.
	var i = a.length;
	if (i != b.length) {
		return false;
	}
	// 0 = false in javascript, while loop FIRST checks if i == 0, then decrements and runs
	while (i--) {
		if (a[i] != b[i]){
			return false;
		}
	}
	return true;
}

function clean_value(x){
  //helper for clear_pos which locks convas lines inside the board. I should make it work for both values at once.
  //case 1: negativ value = set to 0, case 2: value bigger than board = set to max board value.
  if (x < outer_margin) {
    return outer_margin;
  } else if (max_value < x) {
    return max_value;
  } else {
    return x;
  }
}

function draw_board() {
    ctx.fillStyle = "#ac7339";
    ctx.fillRect(0, 0, width, height)
    outer_margin = width * 0.08;
    inner_margin = (width - 2 * outer_margin) / (board_size -1);
    stone_size = inner_margin * 0.48;
    max_value = width - outer_margin;
    //paths of earlier board sizes are still saved? Therefore every board size gets painted at stroke I guess. -> begin&closePath was missing.
    ctx.beginPath();
    for (let i = 0; i < board_size; i += 1) {
    ctx.moveTo(outer_margin, outer_margin + inner_margin * i);
    ctx.lineTo(width - outer_margin, outer_margin + inner_margin * i);
    ctx.moveTo(outer_margin + inner_margin * i , outer_margin);
    ctx.lineTo(outer_margin + inner_margin * i, height - outer_margin);
    }
    ctx.closePath();
    ctx.stroke();
}
