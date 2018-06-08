import React from "react";
import ReactDOM from "react-dom";
import swal from "sweetalert2";
import "regenerator-runtime/runtime";
import BootstrapTable from "react-bootstrap-table-next";
import paginationFactory from "react-bootstrap-table2-paginator";
import "react-bootstrap-table-next/dist/react-bootstrap-table2.min.css";
import DetailsMail from "./DetailsMail";
import ReactTable from "react-table";

import "react-table/react-table.css";


class Sent extends React.Component {
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
            totalSize: 0,
            totalPage: 0
        }
        this.rowEvent = {
            onClick: (e, row, rowIndex) => {
                this.setState({details: true, id:rowIndex});
            }
        };

        this.backButton = this.backButton.bind(this);
        this.fetchData = this.fetchData.bind(this);
    }

    fetchData(state, instance) {
        this.setState({loading: true});
        this.setState({loadingText: "Downloading mails.."});
        this.loadData(state.page + 1);
    }

    backButton(e) {
        e.preventDefault();
        this.setState({details: !this.state.details});
    }

    loadData(page) {
        let url = window.location.pathname + "?page=" + page;
        $.ajax(url, {
            success: function (data) {
                openpgp.initWorker({ path:"/static/js/openpgp.worker.min.js" });
                this.setState({loadingText: "Decrypting mails.."});
                this.setState({sizePerPage: data["sizePerPage"]});
                this.setState({totalSize: data["totalSize"]});
                this.setState({totalPage: data["totalPage"]});
                let bunny = [];
                Promise.all(data["obj"].map(async (hiren, index) => {
                        let bugs = {};
                        let data = {};
                        let privKey = sessionStorage.getItem("private_key");
                        let pubKey = sessionStorage.getItem("public_key");
                        let passphrase = sessionStorage.getItem("passphrase");
                        let privKeyObj = openpgp.key.readArmored(privKey).keys[0];
                        await privKeyObj.decrypt(passphrase);

                        let subject_options = {
                            message: openpgp.message.readArmored(hiren["subject"]),
                            publicKeys: openpgp.key.readArmored(pubKey).keys,
                            privateKeys: [privKeyObj]
                        };
                        let body_options = {
                            message: openpgp.message.readArmored(hiren["body"]),
                            publicKeys: openpgp.key.readArmored(pubKey).keys,
                            privateKeys: [privKeyObj]
                        };

                        let subject = await openpgp.decrypt(subject_options);
                        let body = await openpgp.decrypt(body_options);

                        bugs["id"] = hiren["id"];
                        bugs["mail_from"] = hiren["mail_from"];
                        bugs["mail_to"] = hiren["mail_to"];
                        bugs["bcc"] = hiren["bcc"];
                        bugs["cc"] = hiren["cc"];
                        bugs["subject"] = DOMPurify.sanitize(subject["data"]);
                        bugs["body"] = DOMPurify.sanitize(body["data"]);
                        bugs["attachment"] = hiren["emotional_attachment"];
                        bugs["date"] = hiren["created_at"];
                        bunny.push(bugs);
                    })
                ).then(() => {
                    this.setState({data: bunny});
                    this.setState({loading: false});
                }).catch((err) => {
                    swal("Oops...", "Something went wrong, check console", "error");
                    console.error(err);
                });
            }.bind(this),
            error: function (err) {
                console.error(err);
            }
        });
    }

    componentDidMount() {
        this.loadData(this.state.page);
    }

    render() {
        if (this.state.details) {
            return (
                <DetailsMail data={this.state.data[this.state.id]} backButton={this.backButton}/>
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
                    <ReactTable
                        manual
                        data={this.state.data}
                        columns={this.columns}
                        loading={this.state.loading}
                        loadingText={this.state.loadingText}
                        showPageSizeOptions={false}
                        defaultPageSize={18}
                        showPageJump={false}
                        sortable={false}
                        multiSort={false}
                        resizable={true}
                        filterable={false}
                        pages={this.state.totalPage}
                        onFetchData={this.fetchData}
                        minRows={0}
                    />
                </div>
            </div>
        )
    }

}

ReactDOM.render(<Sent />, document.getElementById("sent"));
