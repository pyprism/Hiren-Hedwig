/**
 * Form body editor
 */
let quill;
function editor() {
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
}

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
function contacts_from() {
    let REGEX_EMAIL = '([a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*@' +
        '(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)';
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
                maxItems: '1',
                persist: false,
                options: mails,
                create: function(input) {
                    return {
                        value: input,
                        text: input
                    }
                },
                createFilter: function(input) {
                    var match, regex;

                    // email@address.com
                    regex = new RegExp('^' + REGEX_EMAIL + '$', 'i');
                    match = input.match(regex);
                    if (match) return !this.options.hasOwnProperty(match[0]);

                    // name <email@address.com>
                    regex = new RegExp('^([^<]*)\<' + REGEX_EMAIL + '\>$', 'i');
                    match = input.match(regex);
                    if (match) return !this.options.hasOwnProperty(match[2]);

                    return false;
                },
            })
        },
        error: function (err) {
            console.error(err);
        }
    });
}

function contacts_to() {
    let REGEX_EMAIL = '([a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*@' +
        '(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)';
    let mails = [];
    $.ajax({
        type: "GET",
        url: "/contact_ajax/to/",
        success: function (data) {
            data.forEach(function (yo) {
                if(yo["fields"]["name"]){
                    let bunny = {'value': '', 'text': ''};
                    bunny['value'] = yo["fields"]["email"];
                    bunny['text'] = yo["fields"]["name"];
                    mails.push(bunny);
                } else {
                    let only_email = {"value": "", "text": ""};
                    only_email["value"] = yo["fields"]["email"];
                    only_email["text"] = yo["fields"]["email"];
                    mails.push(only_email);
                }
            });

            $('#to').selectize({
                delimiter: ',',
                persist: false,
                options: mails,
                valueField: 'value',
                labelField: 'text',
                searchField: ['value', 'text'],
                create: function(input) {
                    return {
                        value: input,
                        text: input
                    };
                },
                createFilter: function(input) {
                    let match, regex;

                    // email@address.com
                    regex = new RegExp('^' + REGEX_EMAIL + '$', 'i');
                    match = input.match(regex);
                    if (match) return !this.options.hasOwnProperty(match[0]);

                    // name <email@address.com>
                    regex = new RegExp('^([^<]*)\<' + REGEX_EMAIL + '\>$', 'i');
                    match = input.match(regex);
                    if (match) return !this.options.hasOwnProperty(match[2]);

                    return false;
                },
            });

            $('#bcc').selectize({
                delimiter: ',',
                persist: false,
                options: mails,
                valueField: 'value',
                labelField: 'text',
                searchField: ['value', 'text'],
                create: function(input) {
                    return {
                        value: input,
                        text: input
                    };
                },
                createFilter: function(input) {
                    var match, regex;

                    // email@address.com
                    regex = new RegExp('^' + REGEX_EMAIL + '$', 'i');
                    match = input.match(regex);
                    if (match) return !this.options.hasOwnProperty(match[0]);

                    // name <email@address.com>
                    regex = new RegExp('^([^<]*)\<' + REGEX_EMAIL + '\>$', 'i');
                    match = input.match(regex);
                    if (match) return !this.options.hasOwnProperty(match[2]);

                    return false;
                },
            });
            $('#cc').selectize({
                delimiter: ',',
                persist: false,
                options: mails,
                valueField: 'value',
                labelField: 'text',
                searchField: ['value', 'text'],
                create: function(input) {
                    return {
                        value: input,
                        text: input
                    };
                },
                createFilter: function(input) {
                    let match, regex;

                    // email@address.com
                    regex = new RegExp('^' + REGEX_EMAIL + '$', 'i');
                    match = input.match(regex);
                    if (match) return !this.options.hasOwnProperty(match[0]);

                    // name <email@address.com>
                    regex = new RegExp('^([^<]*)\<' + REGEX_EMAIL + '\>$', 'i');
                    match = input.match(regex);
                    if (match) return !this.options.hasOwnProperty(match[2]);

                    return false;
                },
            });
        },
        error: function (err) {
            console.error(err);
        }
    });
}

window.onload = function () {
    contacts_from();
    contacts_to();
    editor();
};
