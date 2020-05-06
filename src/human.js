click_listener = (x, y) => { };
highlight_y = -1;
highlight_x = -1;

function clicklistener(x, y) {
    var result = null;
    console.log(x < 4);
    console.log(is_first);
    if ((x < 4) ^ (is_first)) {
        result = [y, x];
    } else {
        result = board_obj.available;
        y = result[0];
        x = result[1];
    }
    console.log(result);
    var id = "tile" + String(x) + String(y);
    var e = document.getElementById(id);
    console.log(e);
    e.classList.remove("free");
    setTimeout('document.getElementById("' + id + '").classList.add("free")', 300);
    ws.send(JSON.stringify({ "action": result }));
    disable_click();
}

function keylistener(event) {
    var e = event || window.event;
    console.log(e.key);
    action = null;
    if (e.key == "ArrowUp") {
        action = 0;
    } else if (e.key == "ArrowDown") {
        action = 1;
    } else if (e.key == "ArrowLeft") {
        action = 2;
    } else if (e.key == "ArrowRight") {
        action = 3;
    }
    if (action != null) {
        ws.send(JSON.stringify({ "action": action }));
        disable_key();
    } else {
        alert("Select a direction");
    }
}

function disable_click() {
    click_listener = (x, y) => { };
}
function enable_click() {
    click_listener = clicklistener;
}
function disable_key() {
    document.querySelector("body").onkeydown = (e) => { };
}
function enable_key() {
    document.querySelector("body").onkeydown = keylistener;
}

function render(board_obj) {
    round = board_obj.current_round;
    mode = board_obj.mode;
    board = board_obj.board;

    document.getElementById("round").innerText = "Current Round: " + String(round);

    if (mode == "direction") {
        enable_key();
    } else {
        enable_click();
    }

    board.split("\n").forEach((value, index) => {
        if (index >= 4) { return; }
        value.split(" ").forEach((val, ind) => {
            if (ind >= 8) { return; }
            var style = "belongs-to-0";
            if (val[0] == "-") {
                style = "belongs-to-1";
            }
            var v = "<p></p>";
            if (Number(val.slice(1)) != 0) {
                v = "<p>" + String(Math.pow(2, Number(val.slice(1)))) + "</p>";
            } else {
                style += " free";
            }
            var x = ind;
            var y = index;
            var id = "tile" + String(x) + String(y);
            try {
                document.getElementById(id).innerHTML = v;
                document.getElementById(id).className = style;
            } catch (error) {
                console.log(x, y, id, val, value, current, boards[current]);
            }
        });
    });
    if (board_obj.available.length == 2) {
        // available block in my region
        var highlight_x = board_obj.available[1];
        var highlight_y = board_obj.available[0];
        var id = "tile" + String(highlight_x) + String(highlight_y);
        document.getElementById(id).classList.add("highlight");
    } else {
        // var id = "tile" + String(highlight_x) + String(highlight_y);
        // document.getElementById(id).classList.remove("highlight");
        // highlight_x = -1;
        // highlight_y = -1;
    }
}