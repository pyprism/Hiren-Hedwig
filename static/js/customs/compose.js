/**
 * Form body editor
 */
let quill;
window.onload = function () {
    quill = new Quill('#mailBody', {
        modules: {
            toolbar: [
                [{ 'header': '1'}, {'header': '2'}, { 'font': [] }],
                [{size: []}],
                ['bold', 'italic', 'underline', 'strike', 'blockquote'],
                [{'list': 'ordered'}, {'list': 'bullet'},
                    {'indent': '-1'}, {'indent': '+1'}],
                ['link', 'image', 'video'],
            ],
            clipboard: {
                // toggle to add extra line breaks when pasting HTML:
                matchVisual: false,
            }
        },
        theme: 'snow'
    });
};

let form = document.querySelector('form');
form.onsubmit = function() {
    // Populate hidden form on submit
    let body = document.querySelector('input[name=body]');
    body.value = quill.root.innerHTML;
    return true;
};

/**
 * Contact list generator
 */
(function contacts_from() {
    let mails = [];
    $.ajax({
        type: "GET",
        url: "/contact_ajax/",
        success: function (data) {
            data.forEach(function (yo) {
                let bunny = {'value': '', 'text': ''};
                bunny['value'] = yo["fields"]["email"];
                bunny['text'] = yo["fields"]["email"];
                mails.push(bunny);
            })

            $('#from').selectize({
                delimiter: ';',
                maxItems: 1,
                persist: false,
                options: mails,
                create: function(input) {
                    return {
                        value: input,
                        text: input
                    }
                }
            })
        },
        error: function (err) {
            console.error(err);
        }
    });
})();