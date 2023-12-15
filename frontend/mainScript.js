
document.addEventListener('DOMContentLoaded', function() {

    var talkButton = document.querySelector('.talk-button');

    talkButton.addEventListener('click', function() {
      window.location.href = 'modal.html';
    });
  });