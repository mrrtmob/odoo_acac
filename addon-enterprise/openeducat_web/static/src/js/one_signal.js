odoo.define("openeducat_web.one_signal", function(require) {
    "use strict";
    var utils = require('web.utils');
    var session = require('web.session');

    $(document).ready(function (require) {
        //Setting User ID In cookie For One Signal
        utils.set_cookie('user_id', session.uid);
    });
});