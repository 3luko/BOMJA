const eventImageInput = document.getElementById("eventImage");
const eventImagePreview = document.getElementById("eventImagePreview");

if (eventImageInput && eventImagePreview) {
    eventImageInput.addEventListener("change", function () {
        const file = this.files[0];

        if (!file) {
            eventImagePreview.src = "";
            eventImagePreview.style.display = "none";
            return;
        }

        const imageURL = URL.createObjectURL(file);

        eventImagePreview.src = imageURL;
        eventImagePreview.style.display = "block";
    });
}