odoo.define('pm_rest_api.backlink', function(require) {
"use strict";
var rpc = require('web.rpc')
var core = require('web.core')
var Widget = require('web.Widget');

document.getElementById('deep_link').onclick = function(){
     window.location = 'fb://profile';
}

var HomeCustom =  Widget.extend({
    template: 'HomeCustom',
    start: function() {
            this.$el.append($('<div>').text('Hello dear Odoo user!'));
        },
    events: {
        'click .deep_link_button': 'goToApp',
    },
    goToApp: function (ev) {
        alert("HEHE SAD")
    }
});

core.action_registry.add('auth_signup.reset_password', HomeCustom);
return HomeCustom
});
