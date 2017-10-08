function clearLog() {
    var success = function () {
        location.reload();
    };
    Ajax.post("","", success)
}