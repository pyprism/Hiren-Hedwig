import React from "react";
import ReactDOM from "react-dom";
import swal from "sweetalert2";
import "regenerator-runtime/runtime";
import ReactQuill from 'react-quill';


class Compose extends React.Component {
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


    handleFromChange(event) {
        this.setState({from: event.target.value});
    }

    handleToChange(event) {
        this.setState({to: event.target.value});
    }

    handleCcChange(event) {
        this.setState({cc: event.target.value});
    }

    handleBccChange(event) {
        this.setState({bcc: event.target.value});
    }

    handleSubjectChange(event) {
        this.setState({subject: event.target.value});
    }

    handleBodyChange(bunny) {
        this.setState({body: bunny});
    }

    handleAttachmentChange(event) {
        this.setState({attachment: event.target.value});
    }

    handleSubmit(event) {
        event.preventDefault();
    }

    handleDraft(event) {
        event.preventDefault();
    }

    render() {

        const {from, to, bcc, cc, body, subject, attachment} = this.state;

        return(
            <form className="form-horizontal" onSubmit={this.handleSubmit.bind(this)}>
                <div className="row clearfix">
                    <div className="col-lg-2 col-md-2 col-sm-4 col-xs-5 form-control-label">
                        <label>From</label>
                    </div>
                    <div className="col-lg-10 col-md-10 col-sm-8 col-xs-7">
                        <div className="form-group">
                            <div className="form-line">
                                <input type="text" required value={from} onChange={this.handleFromChange.bind(this)} className="form-control" placeholder="mail@yourmailgundomain.com"/>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="row clearfix">
                    <div className="col-lg-2 col-md-2 col-sm-4 col-xs-5 form-control-label">
                        <label>To</label>
                    </div>
                    <div className="col-lg-10 col-md-10 col-sm-8 col-xs-7">
                        <div className="form-group">
                            <div className="form-line">
                                <input type="text" required value={to} onChange={this.handleToChange.bind(this)} className="form-control" placeholder="Type recipients email"/>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="row clearfix">
                    <div className="col-lg-2 col-md-2 col-sm-4 col-xs-5 form-control-label">
                        <label>CC</label>
                    </div>
                    <div className="col-lg-10 col-md-10 col-sm-8 col-xs-7">
                        <div className="form-group">
                            <div className="form-line">
                                <input type="text"  value={cc} onChange={this.handleCcChange.bind(this)} className="form-control" placeholder="Optional CC"/>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="row clearfix">
                    <div className="col-lg-2 col-md-2 col-sm-4 col-xs-5 form-control-label">
                        <label>BCC</label>
                    </div>
                    <div className="col-lg-10 col-md-10 col-sm-8 col-xs-7">
                        <div className="form-group">
                            <div className="form-line">
                                <input type="text" value={bcc} onChange={this.handleBccChange.bind(this)} className="form-control" placeholder="Optional BCC"/>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="row clearfix">
                    <div className="col-lg-2 col-md-2 col-sm-4 col-xs-5 form-control-label">
                        <label>Subject</label>
                    </div>
                    <div className="col-lg-10 col-md-10 col-sm-8 col-xs-7">
                        <div className="form-group">
                            <div className="form-line">
                                <input type="text" required value={subject} onChange={this.handleSubjectChange.bind(this)} className="form-control" placeholder="Type subject"/>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="row clearfix">
                    <div className="col-lg-2 col-md-2 col-sm-4 col-xs-5 form-control-label">
                        <label>Body</label>
                    </div>
                    <div className="col-lg-10 col-md-10 col-sm-8 col-xs-7">
                        <div className="form-group">
                            <div className="form-line">
                                <ReactQuill
                                    value={body}
                                    onChange={this.handleBodyChange.bind(this)}
                                    modules={ReactQuill.modules}
                                    formats={ReactQuill.formats}
                                    placeholder={"Type mail body..."}
                                />
                            </div>
                        </div>
                    </div>
                </div>
                <div className="row clearfix">
                    <div className="col-lg-2 col-md-2 col-sm-4 col-xs-5 form-control-label">
                        <label>Attachment</label>
                    </div>
                    <div className="col-lg-10 col-md-10 col-sm-8 col-xs-7">
                        <div className="form-group">
                            <input type="file" value={attachment} onChange={this.handleAttachmentChange.bind(this)} className="form-control" multiple/>
                        </div>
                    </div>
                </div>
                <div className="row clearfix">
                    <div className="col-lg-offset-2 col-md-offset-2 col-sm-offset-4 col-xs-offset-5">
                        <button type="submit" className="btn btn-success m-t-15 waves-effect">
                            <i className="material-icons">send</i>
                            <span>Send</span>
                        </button>
                        <button type="button" onClick={this.handleDraft.bind(this)} className="btn btn-info m-t-15 waves-effect">
                            <i className="material-icons">drafts</i>
                            <span>Draft</span>
                        </button>
                    </div>
                </div>
            </form>
        )
    }
}


ReactQuill.modules = {
  toolbar: [
    [{ 'header': '1'}, {'header': '2'}, { 'font': [] }],
    [{size: []}],
    ['bold', 'italic', 'underline', 'strike', 'blockquote'],
    [{'list': 'ordered'}, {'list': 'bullet'},
     {'indent': '-1'}, {'indent': '+1'}],
    ['link', 'image', 'video'],
    ['clean']
  ],
  clipboard: {
    // toggle to add extra line breaks when pasting HTML:
    matchVisual: false,
  }
}

ReactQuill.formats = [
  'header', 'font', 'size',
  'bold', 'italic', 'underline', 'strike', 'blockquote',
  'list', 'bullet', 'indent',
  'link', 'image', 'video',
]


ReactDOM.render(<Compose />, document.getElementById("compose"));

