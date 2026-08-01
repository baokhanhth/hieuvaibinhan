const password = document.querySelector(
    "input[type=password]"
);

password.addEventListener("keypress",(e)=>{

    if(e.key==="Enter"){

        document.querySelector("form").submit();

    }

});