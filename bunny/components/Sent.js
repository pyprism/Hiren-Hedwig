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
        this.products = [
            {"id": 1, "name": "Xxx", "price": "521$", "date": ""},
            {"id": 2, "name": "444", "price": "421$", "date": "sss"},
        ];
        this.columns = [{
            dataField: 'id',
            text: 'From'
        }, {
            dataField: 'name',
            text: 'To'
        }, {
            dataField: 'price',
            text: 'Subject'
        },
            {
                dataField: "date",
                text: "Date"
            }];
        this.state = {
            from: "",
            to: "",
            cc: [],
            bcc: [],
            subject: "",
            body: "",
            attachment: "",
            loading: true,
            loadingText: "Downloading..",
            data: ""
        };
    }

    componentDidMount() {
        $.ajax(window.location.pathname, {
            success: function (data) {
                //console.log(data);
                //console.log(data["obj"].length);
                let bunny = [];
                Promise.all(data["obj"].map(async (hiren, index) => {
                        let bugs = {};
                        openpgp.initWorker({ path:"/static/js/openpgp.worker.min.js" });
                        let data = {};
                        let privKey = sessionStorage.getItem("private_key");
                        let pubKey = sessionStorage.getItem("public_key");
                        let passphrase = sessionStorage.getItem("passphrase");
                        //console.log(privKey);
                        //console.log(pubKey);
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
                        // openpgp.decrypt(subject_options).then(function(plaintext) {
                        //     console.log(plaintext.data);
                        //     return plaintext.data;
                        // });
                        let subject = await openpgp.decrypt(subject_options);
                        let body = await openpgp.decrypt(body_options);
                        console.log(subject["data"]);
                        console.log(DOMPurify.sanitize(body["data"]));
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

    render() {
        return(
            <BootstrapTable
                remote
                keyField='id'
                data={ this.products }
                columns={ this.columns }
            />
        )
    }

}

ReactDOM.render(<Sent />, document.getElementById("sent"));
