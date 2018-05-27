import React from "react";
import ReactDOM from "react-dom";
import swal from "sweetalert2";
import "regenerator-runtime/runtime";
import BootstrapTable from "react-bootstrap-table-next";
import paginationFactory from "react-bootstrap-table2-paginator";
import "react-bootstrap-table-next/dist/react-bootstrap-table2.min.css";
import DetailsMail from "./DetailsMail";


class Sent extends React.Component {
    constructor(prop) {
        super(prop);
        this.columns = [{
            dataField: 'mail_from',
            text: 'From'
        }, {
            dataField: 'subject',
            text: 'Subject'
        }, {
            dataField: "date",
            text: "Date"
        }];
        this.state = {
            loading: true,
            loadingText: "Downloading mails..",
            data: "",
            details: false,
            id: 0,
            page: 1,
            sizePerPage: 0,
            totalSize: 0
        }
        this.rowEvent = {
            onClick: (e, row, rowIndex) => {
                this.setState({details: true, id:rowIndex});
            }
        };
        this.onTableChange = (type, { page, sizePerPage }) => {
            this.setState({loading: true});
            this.setState({loadingText: "Downloading mails.."});
            this.setState({page: page});
            this.loadData(page);
        };
        this.selectRow = {
            mode: 'checkbox',
            clickToSelect: false,
            // onSelect: (row, isSelect, rowIndex, e) => {
            //     console.log(isSelect, rowIndex, e);
            // }
        }

        this.backButton = this.backButton.bind(this);
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
        if (this.state.loading) {
            return (
                <div className="card">
                    <div className="header">
                        <h2>
                            Sent Mail
                        </h2>
                    </div>
                    <div className="body">
                        <div className="text-center">{this.state.loadingText}</div>
                    </div>
                </div>

            )
        } else {
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
                        <BootstrapTable
                            remote
                            striped
                            hover
                            condensed
                            //bordered={false}
                            pagination={ paginationFactory({
                                page: this.state.page,
                                sizePerPage: this.state.sizePerPage,
                                totalSize: this.state.totalSize,
                                hideSizePerPage: true,
                                hidePageListOnlyOnePage: true,
                            }) }
                            keyField='id'
                            data={this.state.data}
                            columns={this.columns}
                            selectRow={ this.selectRow }
                            rowEvents={this.rowEvent}
                            noDataIndication="Mailbox is empty"
                            onTableChange={ this.onTableChange }
                        />
                    </div>
                </div>
            )
        }
    }

}

ReactDOM.render(<Sent />, document.getElementById("sent"));
