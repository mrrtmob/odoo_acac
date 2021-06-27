odoo.define('openeducat_skill_enterprise.tour', function (require) {
'use strict';

var tour = require("web_tour.tour");

tour.register('skill_portal', {
    test: true,
    url: '/student/skill',
},
    [
        {
            content: "Add new shipping address",
            trigger: 'form[action^="/student/skill/submit"]',
        },
    ]
);

});
