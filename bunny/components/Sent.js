import React from "react";
import ReactDOM from "react-dom";
import swal from "sweetalert2";
import "regenerator-runtime/runtime";
import BootstrapTable from "react-bootstrap-table-next";
import paginationFactory from "react-bootstrap-table2-paginator";
import "react-bootstrap-table-next/dist/react-bootstrap-table2.min.css";


class Sent extends React.Component {
    constructor(prop) {
        super(prop);
        this.columns = [{
            dataField: 'mail_from',
            text: 'From'
        }, {
            dataField: 'mail_to',
            text: 'To'
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
            data: ""
        };
    }

    componentDidMount() {
        $.ajax(window.location.pathname, {
            success: function (data) {
                //console.log(data);
                this.setState({loadingText: "Decrypting mails.."});
                let bunny = [];
                Promise.all(data["obj"].map(async (hiren, index) => {
                        let bugs = {};
                        openpgp.initWorker({ path:"/static/js/openpgp.worker.min.js" });
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
                    //swal("Oops...", "Secret key is not correct!", "error");
                    console.error(err);
                });
            }.bind(this),
            error: function (err) {
                console.error(err);
            }
        });
    }

    rowEvent() {
        onClick: (e, row, rowIndex) => {
            console.info(e, row, rowIndex);
        }
    }

    render() {
        if (this.state.loading) {
            return (
                <div className="text-center">{this.state.loadingText}</div>
            )
        }
        return(
            <BootstrapTable
                remote
                striped
                hover
                condensed
                keyField='id'
                data={ this.state.data }
                columns={ this.columns }
                rowEvents={ this.rowEvents }
            />
        )
    }

}

ReactDOM.render(<Sent />, document.getElementById("sent"));
