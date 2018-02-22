import React, { Component } from "react";
import ReactDOM from "react-dom";

class Inbox extends Component {

    constructor(props){
        super(props);
        this.loadData();
        this.state = {
            thread: []
        }
    }

    loadData() {
        $.ajax('/mail/inbox/', {
            contentType: 'application/json',
            success: function(data) {
                console.log(data);
            },
            error: function(data) {
                console.error(data);
            }
        });
    }

    render() {
        return (
            <div>
                Hellos
            </div>
        );
    }
}

ReactDOM.render(<Inbox />, document.getElementById('inbox'));