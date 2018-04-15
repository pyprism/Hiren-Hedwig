import swal from "sweetalert2";

window.onload = function () {
    if(!sessionStorage["private_key"] || !sessionStorage["public_key"]) {
        swal("Opps..", "Keys are empty, Reenter?", "error").then(() => {
            window.location.replace("/unlock/");
        });
    }
};