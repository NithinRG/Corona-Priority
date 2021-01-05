const navFunction = () => {
    const burger = document.querySelector(".burger")
    const nav = document.querySelector(".nav-items")
    const navItems = document.querySelectorAll(".nav-items li")

    burger.addEventListener('click', () => {
        nav.classList.toggle("nav-active");
        navItems.forEach((item,index) => {
            if (item.style.animation) {
                item.style.animation = ``
            } else {
                item.style.animation = `navFadeIn 0.5s ease forwards ${index/10 + 0.3}s`
            }
        });
        burger.classList.toggle("toggle");
    });
}

navFunction();



