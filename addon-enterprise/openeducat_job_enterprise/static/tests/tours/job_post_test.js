odoo.define('openeducat_job_enterprise.tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('test_job', {
    test: true,
    url: '/job_post/detail/1',
},
    [
        {
            content: "select Application Engineer",
            extra_trigger: '#job_post_field',
            trigger: 'span:contains(Application Engineer)',
        },
    ]
);

});
