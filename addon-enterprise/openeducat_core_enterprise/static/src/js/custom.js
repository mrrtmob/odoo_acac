odoo.define('openeducat_core_enterprise.batch_on_courses', function (require) {
    "use strict";

    var core = require('web.core');
    var Dialog = require("web.Dialog");
    var session = require('web.session');
    var ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var websiteRootData = require('website.root');
    var utils = require('web.utils');
    var _t = core._t;
    var qweb = core.qweb;

    var SubjectRegister = Widget.extend({
        events:{'change #course_dropdown': '_onchangedropdown'},
        xmlDependencies: ['/openeducat_core_enterprise/static/src/xml/custom.xml'],

        init: function(){
            this._super.apply(this,arguments);
        },
        start: function () {
            return this._super();
        },
        _onchangedropdown: function(ev){
            console.log("list item selected",$(ev.currentTarget).val());
            var course_id = $(ev.currentTarget).val();
            console.log(course_id);
            ajax.jsonRpc('/get/course_data', 'call',
                {
                'course_id': course_id,
                }).then(function (data) {
                if (data)
                {
                var batch_data = qweb.render('GetBatchData',
                {
                    batches: data['batch_list'],

                });
                $('.batches').html(batch_data);

                if(data)
                var subject_data = qweb.render('GetSubjectData',
                {
                    subjects: data['subject_list']
                });
                $('.subjects').html(subject_data);

                }
                });
        }

    });
    websiteRootData.websiteRootRegistry.add(SubjectRegister, '.js_get_data');
});