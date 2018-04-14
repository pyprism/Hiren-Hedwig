import swal from "sweetalert2";

window.onload = function () {
    if(!sessionStorage["private_key"] || !sessionStorage["public_key"]) {
        swal("Opps..", "Keys are empty, Renter?", "error").then(() => {
            window.location.replace("/unlock/");
        });
    }
};