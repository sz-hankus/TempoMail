function updateTimers() {
    let now = new Date().getTime();
    let timers = document.getElementsByClassName("timer");

    let i = timers.length;
    while (i--) {
        let element = timers[i];
        // JS tmstmp is in milliseconds
        let tmstmp = parseFloat(element.getAttribute("data-expiryTmstmp")) * 1000
        let expiryTime = new Date(tmstmp).getTime();

        let diff = Math.floor((expiryTime - now) / 1000)
        let minutesLeft = Math.floor(diff / 60);
        let secondsLeft = diff % 60;
        if (minutesLeft <= 0 && secondsLeft <= 0) {
            element.parentElement.parentElement.remove();
        }
        element.children.namedItem("minutes").innerText = minutesLeft.toString().padStart(2, '0');
        element.children.namedItem("seconds").innerText = secondsLeft.toString().padStart(2, '0');
    }
}
updateTimers()
setInterval(updateTimers, 1000);