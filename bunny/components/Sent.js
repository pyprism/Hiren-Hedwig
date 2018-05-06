import React from "react";
import ReactDOM from "react-dom";
import swal from "sweetalert2";
import "regenerator-runtime/runtime";


class Sent extends React.Component {
    constructor() {
        super();
        this.state = {
            from: "",
            to: "",
            cc: [],
            bcc: [],
            subject: "",
            body: "",
            attachment: ""
        }
    }

}

ReactDOM.render(<Sent />, document.getElementById("sent"));
