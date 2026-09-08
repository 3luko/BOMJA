

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

// Mobile navigation
const menuToggle = document.querySelector('.menu-toggle');
const mobileMenu = document.querySelector('.mobile-menu');

if (menuToggle && mobileMenu) {
    menuToggle.addEventListener('click', () => {
        const isOpen = mobileMenu.classList.toggle('is-open');
        menuToggle.classList.toggle('is-open', isOpen);
        menuToggle.setAttribute('aria-expanded', String(isOpen));
        menuToggle.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
    });

    mobileMenu.querySelectorAll('a').forEach((link) => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('is-open');
            menuToggle.classList.remove('is-open');
            menuToggle.setAttribute('aria-expanded', 'false');
            menuToggle.setAttribute('aria-label', 'Open navigation');
        });
    });
}

// Keep each carousel's controls connected to its own track.
function setupCarousel(trackSelector, buttonSelector) {
    const track = document.querySelector(trackSelector);
    const buttons = document.querySelectorAll(buttonSelector);

    if (!track || buttons.length === 0) {
        return;
    }

    buttons.forEach((button) => {
        button.addEventListener('click', () => {
            const eventCard = track.querySelector('.event');
            const gap = 24;
            const cardWidth = eventCard
                ? eventCard.getBoundingClientRect().width + gap
                : track.clientWidth * 0.82;
            const direction = button.classList.contains('event-scroll-prev')
                || button.classList.contains('gallery-scroll-prev') ? -1 : 1;

            track.scrollBy({
                left: cardWidth * direction,
                behavior: 'smooth'
            });
        });
    });
}

setupCarousel('.event-track', '.event-controls .event-scroll-btn');
setupCarousel('.gallery-event-track', '.gallery-controls .event-scroll-btn');
