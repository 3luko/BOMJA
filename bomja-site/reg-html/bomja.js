

let slideIndex = 0;

const videos = document.querySelectorAll(".social-video");



showSlides();

function showSlides() {
    let slides = document.getElementsByClassName("slides");

    for (let i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }

    slideIndex++;

    if (slideIndex > slides.length) {
        slideIndex = 1;
    }

    slides[slideIndex - 1].style.display = "block";

    setTimeout(showSlides, 4000); // Change image every 4 seconds
}

window.addEventListener("load", () => {
    if (window.instgrm) {
        window.instgrm.Embeds.process();
    }
});


// Intersection Observer to play/pause videos based on visibility
const videoObserver = new IntersectionObserver(
    (entries) => {

        entries.forEach((entry) => {

            const video = entry.target;

            if (entry.isIntersecting) {
                video.play().catch(() => {});
            } else {
                video.pause();
            }

        });

    },
    {
        threshold: 0.6
    }
);

videos.forEach((video) => {
    videoObserver.observe(video);
});