const Home = () => {
    document.querySelectorAll('.shape').forEach(shape => {
        shape.style.setProperty('--random-x', (Math.random() * 2 - 1).toFixed(2));
        shape.style.setProperty('--random-y', (Math.random() * 2 - 1).toFixed(2));
    }); 
    
    document.getElementById('button-user').addEventListener('click', function(event) {
        event.preventDefault();
        window.location.href = '/user';
    });
};

window.addEventListener("load", async function() {
    console.log("home",window.ws);
});

export default Home;