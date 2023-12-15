document.addEventListener('DOMContentLoaded', function() {
    var controlIcon = document.getElementById('controlIcon');
    var bars = document.querySelectorAll('#bars .bar'); 
    var terminalButton = document.getElementById('terminalIcon');

    terminalButton.addEventListener('click', function() {
        window.location.href = 'main.html'; 
    });

    controlIcon.addEventListener('click', function() {
        if (controlIcon.classList.contains('pause-icon')) {
            controlIcon.classList.remove('pause-icon');
            controlIcon.classList.add('play-icon');
            bars.forEach(bar => bar.style.animationPlayState = 'paused'); 
        } else {
            controlIcon.classList.remove('play-icon');
            controlIcon.classList.add('pause-icon');
            bars.forEach(bar => bar.style.animationPlayState = 'running'); 
        }
    });
});
