import React from "react";
import ReactDOM from "react-dom";


class DetailsMail extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            body: { __html: props.data["body"]}
        };
    }

    render() {
        return (
            <React.Fragment>
                <div className="card">
                    <div className="header">
                        <h5>
                            {this.props.data["subject"]}
                        </h5>
                    </div>
                    <div className="body">
                        <div className="row clearfix">
                            <div className="col-xs-12 ol-sm-12 col-md-12 col-lg-12">
                                <div className="panel-group" id="accordion_1" role="tablist"
                                     aria-multiselectable="true">
                                    <div className="panel panel-primary">
                                        <div className="panel-heading" role="tab" id="headingOne_1">
                                            <h4 className="panel-title">
                                                <a role="button" data-toggle="collapse" data-parent="#accordion_1"
                                                   href="#collapseOne_1" aria-expanded="true"
                                                   aria-controls="collapseOne_1">
                                                    <div className="row">
                                                        <div className="col-md-6">{this.props.data["mail_from"]}</div>
                                                        <div className="col-md-6">
                                                            <div className="pull-right">{this.props.data["date"]}</div>
                                                        </div>
                                                    </div>
                                                </a>
                                            </h4>
                                        </div>
                                        <div id="collapseOne_1" className="panel-collapse collapse in"
                                             role="tabpanel" aria-labelledby="headingOne_1">
                                            <div className="row">
                                                <div className="col-md-6">To: {this.props.data["mail_to"]}</div>
                                                <div className="col-md-6">
                                                    <div className="pull-right">
                                                        {/*<a href="#">*/}
                                                            <button type="button"
                                                                    onClick={this.props.backButton}
                                                                    className="btn bg-purple btn-circle waves-effect waves-circle waves-float waves-light"
                                                                    data-toggle="tooltip" data-placement="top"
                                                                    title="Back to previous page">
                                                                <i className="material-icons">arrow_back</i>
                                                            </button>
                                                        {/*</a>*/}
                                                        <a href="#">
                                                            <button type="button"
                                                                    className="btn bg-green btn-circle waves-effect waves-circle waves-float waves-light"
                                                                    data-toggle="tooltip" data-placement="top"
                                                                    title="Reply">
                                                                <i className="material-icons">reply</i>
                                                            </button>
                                                        </a>
                                                        <a href="#">
                                                            <button type="button"
                                                                    className="btn bg-light-blue btn-circle waves-effect waves-circle waves-float waves-light"
                                                                    data-toggle="tooltip" data-placement="top"
                                                                    title="Forward">
                                                                <i className="material-icons">forward</i>
                                                            </button>
                                                        </a>
                                                        <a href="#">
                                                            <button type="button"
                                                                    className="btn bg-red btn-circle waves-effect waves-circle waves-float waves-light"
                                                                    data-toggle="tooltip" data-placement="top"
                                                                    title="Delete">
                                                                <i className="material-icons">delete_forever</i>
                                                            </button>
                                                        </a>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="panel-body">
                                                <div dangerouslySetInnerHTML={this.state.body}/>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </React.Fragment>
        )
    }
}

export default DetailsMail;
