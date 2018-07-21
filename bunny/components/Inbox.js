import React from "react";
import ReactDOM from "react-dom";
import "regenerator-runtime/runtime";
import swal from "sweetalert2";
import ReactTable from "react-table";
import "react-table/react-table.css";

class Inbox extends React.Component {
    constructor(prop) {
        super(prop);
        this.columns = [{
            Header: 'From',
            accessor: 'mail_from'
        }, {
            accessor: 'subject',
            Header: 'Subject'
        }, {
            accessor: "date",
            Header: "Date"
        }];
        this.state = {
            loading: true,
            loadingText: "Downloading mails..",
            data: [],
            details: false,
            id: 0,
            page: 1,
            sizePerPage: 0,
            totalPage: 0,
            selection: [],
            selectAll: false
        }
        this.rowEvent = {
            onClick: (e, row, rowIndex) => {
                this.setState({details: true, id:rowIndex});
            }
        };

        this.backButton = this.backButton.bind(this);
        this.fetchData = this.fetchData.bind(this);
    }

    loadData(page) {
        let url = window.location.pathname + "?page=" + page;
        $.ajax(url, {
            success: function (data) {
                console.log(data);
            }.bind(this),
            error: function (error) {
                console.error(error);
            }
        });
    }

    componentDidMount() {
        openpgp.initWorker({ path:"/static/js/openpgp.worker.min.js" });
        this.loadData(this.state.page);
    }

    render() {
        if (this.state.details) {
            return (
                <div>details todo</div>
            )
        }
        return (
            <div className="card">
                <div className="header">
                    <h2>
                        Sent Mail
                    </h2>
                </div>
                <div className="body">
                </div>
            </div>
        )
    }
}

ReactDOM.render(<Inbox />, document.getElementById("inbox"));
