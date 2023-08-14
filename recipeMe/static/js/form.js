const popup = document.getElementById('popup');

setTimeout(() => {
  popup.classList.add('active');
}, 100);

setTimeout(() => {
  popup.classList.remove('active');
}, 5100);
