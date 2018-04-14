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
        this.setState({"button": "Verifying"});

        openpgp.initWorker({ path:"/static/js/openpgp.worker.min.js" });
        $.ajax(window.location.pathname, {
            contentType: "application/json",
            success: function (data) {
                console.log(data);
            }
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
