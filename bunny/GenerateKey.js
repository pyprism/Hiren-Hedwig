import React from "react";
import ReactDOM from "react-dom";
import swal from "sweetalert2";


class GenerateKey extends React.Component {

    constructor() {
        super();
        this.state = {
            key: "",
            repeat_key: "",
            button: "Generate"
        }
    }

    handleKeyChange(event){
        this.setState({key: event.target.value});
    }

    handleRepeatKeyChange(event){
        this.setState({repeat_key: event.target.value});
    }

    handleSubmit(event){
        event.preventDefault();
        let csrfcookie = function() {
            let cookieValue = null,
                name = "csrftoken";
            if (document.cookie && document.cookie !== "") {
                let cookies = document.cookie.split(";");
                for (let i = 0; i < cookies.length; i++) {
                    let cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) == (name + "=")) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        };
        if(this.state.key === this.state.repeat_key){
            openpgp.initWorker({ path:"/static/js/openpgp.worker.min.js" });
            let options = {
                userIds: [{ name:"", email:"" }],
                numBits: 2048,
                passphrase: this.state.key
            };

            this.setState({"button": "Generating"});

            openpgp.generateKey(options).then(function(key) {
                const privkey = key.privateKeyArmored;
                const pubkey = key.publicKeyArmored;
                $.ajax({
                    type: "POST",
                    beforeSend: function(request, settings) {
                        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                            request.setRequestHeader("X-CSRFToken", csrfcookie());
                        }
                    },
                    url: window.location.pathname,
                    data: {
                        "public_key": pubkey
                    },
                    success: function (data) {
                        if(data === "success"){
                            this.setState({key: "", repeat_key: "", button: "Done"});
                            sessionStorage.setItem("key", privkey);
                            swal("Success", "Key generated and saved.", "success").then(() => {
                                window.location.replace("/mail/inbox/");
                            });
                        } else {
                            console.error(data);
                            swal("Oops...", "Something went wrong!", "error");
                        }
                    }.bind(this)
                });
            }.bind(this));

        } else {
            this.setState({key: "", repeat_key: ""});
            swal("Oops...", "Key doesn't match, try again.", "error");
        }
    }

    render() {

        const {key, repeat_key, button} = this.state;

        return (
            <form id="sign_in" onSubmit={this.handleSubmit.bind(this)}>
                <div className="msg">Create new encryption key</div>
                <div className="input-group">
                        <span className="input-group-addon">
                            <i className="material-icons">lock</i>
                        </span>
                    <div className="form-line">
                        <input type="password" autoFocus value={key} onChange={this.handleKeyChange.bind(this)} className="form-control" placeholder="Encryption key" required/>
                    </div>
                </div>
                <div className="input-group">
                        <span className="input-group-addon">
                            <i className="material-icons">lock</i>
                        </span>
                    <div className="form-line">
                        <input type="password" className="form-control" value={repeat_key} onChange={this.handleRepeatKeyChange.bind(this)} placeholder="Repeat encryption key" required/>
                    </div>
                </div>
                <div className="row">
                    <div className="col-sm-12">
                        <div className="center-block">
                            <button className="btn btn-block bg-green waves-effect" type="submit">{button}</button>
                        </div>
                    </div>
                </div>
            </form>
        )
    }
}

ReactDOM.render(<GenerateKey />, document.getElementById("generate_key"));
