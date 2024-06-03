const Controls = () => {

	document.querySelectorAll('.shape').forEach(shape => {
        shape.style.setProperty('--random-x', (Math.random() * 3 - 1).toFixed(2));
        shape.style.setProperty('--random-y', (Math.random() * 3 - 1).toFixed(2));
    }); 
	
};

document.addEventListener('load', Controls);

export default Controls;