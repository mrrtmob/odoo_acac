odoo.define('openeducat_placement_job_enterprise.tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_activity_announcement_apply', {
    test: true,
    url: '/website/activity/announcement',
},
    [
        {
            content: " go to Activity_detail",
            trigger: "a[href*='/activity/announcement/detail/1']"
        }
    ]
);

});
