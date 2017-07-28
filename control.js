let webSocket = null
let w = a = s = d = 0;

let pressX = pressY = null;
let mouseX = mouseY = 0;
let minRad = 0;
let motorOnBool = false;

window.requestAnimationFrame(loop);

function DrawLine(mouseX, mouseY) {
    let canvas = document.getElementById("canvas");
    let ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    if(gamepad != null && pressX != null && pressY != null) {
        ctx.beginPath();
        ctx.moveTo(pressX, pressY);
        ctx.lineTo(mouseX, mouseY);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.arc(pressX, pressY, Math.max(minRad, Math.sqrt(Math.pow(pressX - mouseX, 2) + Math.pow(pressY - mouseY, 2))), 0, 2*Math.PI);
        ctx.stroke();
    }
}

function sendData(data) {
    if(webSocket.readyState === webSocket.OPEN) {
        webSocket.send(JSON.stringify(data));
    }
}

function controllerData(axisv, axish) {
    let total = Math.max(1, Math.abs(axisv) + Math.abs(axish))

    let ver = axisv;
    let hor = axish;

    let leftpower = (ver + hor) / total || 0;
    let rightpower = (ver - hor) / total || 0;

    if(Math.abs(leftpower < 0.05)) {
        leftpower = 0;
    }

    if(Math.abs(rightpower < 0.05)) {
        rightpower = 0;
    }

    document.getElementById("axis0").innerHTML = leftpower;
    document.getElementById("axis1").innerHTML = rightpower;
    document.getElementById("total").innerHTML = total;

    let data = {
        "moveData": true,
        "left": rightpower,
        "right": leftpower
    };
    return data;
}

function keyboardData(w, a, s, d) {
    let hor = a + d;
    let ver = w + s;

    let total = Math.abs(hor) + Math.abs(ver);

    let leftpower = (ver + hor)/ total || 0;
    let rightpower = (ver - hor) / total || 0;

    document.getElementById("axis0").innerHTML = leftpower;
    document.getElementById("axis1").innerHTML = rightpower;
    document.getElementById("total").innerHTML = total;

    let data = {
        "moveData": true,
        "left": rightpower,
        "right": leftpower
    };

    return data;
}

function loop(time) {
    let gamepad = navigator.getGamepads()[0];

    let data = null;

    if(gamepad != null) {
        document.getElementById("controller").innerHTML = "Controller Detected";  
        data = controllerData(gamepad.axes[1], gamepad.axes[0])
    }
    else if(pressX != null && pressY != null) {
        document.getElementById("mouseX").innerHTML = mouseX;
        document.getElementById("mouseY").innerHTML = mouseY;

        document.getElementById("controller").innerHTML = "Using mouse";
        data = controllerData((mouseY - pressY) / minRad, (mouseX - pressX) / minRad);
    }
    else {
        document.getElementById("controller").innerHTML = "Waiting for controller";
        data = keyboardData(w, a, s, d);
    }

    sendData(data);

    window.requestAnimationFrame(loop);
}

function motorOn(event) {
    let data = {
        "moveData": false,
        "motorOn": true
    };

    sendData(data);
}

function motorOff(event) {
    let data = {
        "moveData": false,
        "motorOn": false
    };

    sendData(data);
}

window.onload=function() {
    console.log("loaded");
    document.getElementById("onButton").addEventListener("click", motorOn);
    document.getElementById("offButton").addEventListener("click", motorOff);
    webSocket = new WebSocket("ws://" + location.host + "/ws");
    console.log(location.host)

    webSocket.addEventListener("message", function(event) {
        console.log("data:" + event.data)
        if(event.data == "on") {
            document.getElementById("motorStatus").className = "motorOn";
            document.getElementById("motorStatus").innerHTML = "ON";
        }
        else if(event.data == "off") {
            document.getElementById("motorStatus").className = "motorOff";
            document.getElementById("motorStatus").innerHTML = "OFF";
        }
    })
};

document.addEventListener("mousemove", function(event) {
    mouseX = event.clientX;
    mouseY = event.clientY;

    let canvas = document.getElementById("canvas");
    canvas.width = document.body.clientWidth;
    canvas.height = document.body.clientHeight;
    minRad = Math.min(canvas.height, canvas.height) / 4;

    if(pressX != null) {
        DrawLine(mouseX, mouseY);
    }
});

document.addEventListener("mousedown", function(event) {
    pressX = event.clientX;
    pressY = event.clientY;
    mouseMode = true;
});

document.addEventListener("mouseup", function(event) {
    pressX = null;
    pressY = null;
    DrawLine(0, 0);
    mouseMode = false;
});

document.addEventListener("touchmove", function(event) {
    mouseX = event.touches[0].clientX;
    mouseY = event.touches[0].clientY;

    let canvas = document.getElementById("canvas");
    canvas.width = document.body.clientWidth;
    canvas.height = document.body.clientHeight;
    minRad = Math.min(canvas.height, canvas.height) / 4;

    if(pressX != null) {
        DrawLine(mouseX, mouseY);
    }
});

document.addEventListener("touchstart", function(event) {
    pressX = event.touches[0].clientX;
    pressY = event.touches[0].clientY;
    mouseMode = true;
});

document.addEventListener("touchend", function(event) {
    pressX = null;
    pressY = null;
    DrawLine(0, 0);
    mouseMode = false;
});

document.addEventListener("keydown", function(event) {
    if (event.keyCode == 87) {
        w = -1;
    }

    if (event.keyCode == 65) {
        a = 1;
    }

    if (event.keyCode == 83) {
        s = 1;
    }

    if (event.keyCode == 68) {
        d = -1;
    }
});

document.addEventListener("keyup", function(event) {
    if (event.keyCode == 87) {
        w = 0;
    }

    if (event.keyCode == 65) {
        a = 0;
    }

    if (event.keyCode == 83) {
        s = 0;
    }

    if (event.keyCode == 68) {
        d = 0;
    }
});

window.addEventListener("gamepaddisconnected", function(e) {
    document.getElementById("controller").innerHTML = "Controller Disconnected";
});