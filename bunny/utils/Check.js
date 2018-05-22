import swal from "sweetalert2";

if (!sessionStorage["private_key"] || !sessionStorage["public_key"]) {
    if (!sessionStorage["passphrase"]) {
        swal("Opps..", "Keys are empty, Re-enter?", "error").then(() => {
            window.location.replace("/unlock/");
        });
    }
}
