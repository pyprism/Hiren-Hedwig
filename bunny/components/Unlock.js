import React from "react";
import ReactDOM from "react-dom";
import swal from "sweetalert2";
import "regenerator-runtime/runtime";

class Unlock extends React.Component {
    constructor() {
        super();
        this.state = {
            key: "",
            button: "Unlock"
        }
    }

    handleKeyChange(event){
        this.setState({key: event.target.value});
    }

    handleSubmit(event) {
        event.preventDefault();
        if((this.state.key).length <= 0){
            return;
        }
        this.setState({"button": "Verifying"});

        openpgp.initWorker({ path:"/static/js/openpgp.worker.min.js" });
        $.ajax(window.location.pathname, {
            contentType: "application/json",
            success: async function (data) {
                let private_key, passphrase;
                let options = {
                    message: openpgp.message.readArmored(data[0]["fields"]["private_key"]),
                    passwords: this.state.key,
                    format: "utf8"
                };
                let passphrase_options = {
                    message: openpgp.message.readArmored(data[0]["fields"]["passphrase"]),
                    passwords: this.state.key,
                    format: "utf8"
                };
                try {
                    private_key = await openpgp.decrypt(options);
                    passphrase = await openpgp.decrypt(passphrase_options);
                } catch(e) {
                    swal("Oops...", "Key is not valid! Try again", "error");
                    this.setState({key:"", button: "Unlock"});
                    return;
                }

                sessionStorage.setItem("private_key", private_key["data"]);
                sessionStorage.setItem("passphrase", passphrase["data"]);
                sessionStorage.setItem("public_key", data[0]["fields"]["public_key"]);
                this.setState({key:"", button: "Verified"});
                window.location.href = "/mail/inbox/";
            }.bind(this)
        });



    }

    render() {
        const {key, button} = this.state;

        return (
            <form id="sign_in" onSubmit={this.handleSubmit.bind(this)}>
                <div className="msg">Unlock Mailbox</div>
                <div className="input-group">
                        <span className="input-group-addon">
                            <i className="material-icons">lock</i>
                        </span>
                    <div className="form-line">
                        <input type="password" autoFocus value={key} onChange={this.handleKeyChange.bind(this)} className="form-control" placeholder="Encryption key" required/>
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

ReactDOM.render(<Unlock />, document.getElementById("unlock"));
