const Credits = () => {

	document.querySelectorAll('.shape').forEach(shape => {
        shape.style.setProperty('--random-x', (Math.random() * 3 - 1).toFixed(2));
        shape.style.setProperty('--random-y', (Math.random() * 3 - 1).toFixed(2));
    }); 

	document.getElementById('btn-pcatapan').addEventListener('click', function(event) {
        window.open('https://github.com/pcatapan')
    });

	document.getElementById('btn-msciacca').addEventListener('click', function(event) {
        window.open('https://github.com/msciacca')
    });

	document.getElementById('btn-aanghel').addEventListener('click', function(event) {
        window.open('https://github.com/irinaanghel')
    });
	
};

document.addEventListener('load', Credits);

export default Credits;