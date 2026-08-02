const password = document.querySelector(
    "input[type=password]"
);

password.addEventListener("keypress",(e)=>{

    if(e.key==="Enter"){

        document.querySelector("form").submit();

    }

});

document.addEventListener("DOMContentLoaded", function () {
    const alerts = document.querySelectorAll(".alert");
    
    if (alerts.length > 0) {
        setTimeout(function () {
            alerts.forEach(function (alert) {
                alert.style.transition = "opacity 0.5s ease, transform 0.5s ease";
                alert.style.opacity = "0";
                alert.style.transform = "translateY(-10px)";
                
                setTimeout(() => alert.remove(), 500);
            });
        }, 1200); 
    }
});