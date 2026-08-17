const form = document.getElementById("uploadForm");
const ticketLink = document.getElementById("ticketLink");

form.addEventListener("submit", function(event){

    if (!ticketLink.value.trim()){
        const continueWithoutLink = confirm(
            "No ticket link was added. Do you want to upload this event anyway?"
        );

        if (!continueWithoutLink){
            event.preventDefault();
        }
    }
})