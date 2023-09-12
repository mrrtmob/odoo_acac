odoo.define('openeducat_placement_job_enterprise.tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_activity_details', {
    test: true,
    url: '/activity/announcement/detail/1',
},
    [
        {
            content: " go to activity_apply",
            trigger: "a[href*='/job/post/apply/']"
        }
    ]
);

});
