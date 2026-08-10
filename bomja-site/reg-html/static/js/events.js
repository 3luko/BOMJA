const upcomingEvents = document.querySelector(".upcoming-events");

if (!upcomingEvents) {
    console.error(".upcoming-events container not found");
} else {
    fetch("static/data/events.json")
        .then(response => {
            if (!response.ok) {
                throw new Error("Could not load events.json");
            }

            return response.json();
        })
        .then(events => {
            events.forEach(event => {
                const img = document.createElement("img");

                img.src = `static/uploads/${event.image}`;
                img.alt = event.alt || "BOMJA upcoming event flyer";
                img.loading = "lazy";

                upcomingEvents.appendChild(img);
            });
        })
        .catch(error => {
            console.error("Error loading events:", error);
        });
}