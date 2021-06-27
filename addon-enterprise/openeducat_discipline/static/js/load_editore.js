odoo.define('openeducat_discipline.discipline_editor', function (require) {
    'use strict';

    require('web.dom_ready');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var wUtils = require('website.utils');
    var ajax = require('web.ajax');


    var base = require('web_editor.base');
    var sAnimation = require('website.content.snippets.animation');

    var _t = core._t
    var qweb = core.qweb

    $("document").ready(function () {
        var myElement = document.querySelector("header > .navbar-default");
        // var headroom = new Headroom(myElement);

        // headroom.init();
        $('textarea.load_editor').each(function () {
        var $textarea = $(this);
        if (!$textarea.val().match(/\kkkkkkkkkkkkkkkkkkkkkkkkkkkk5S/)) {
        $textarea.val("");
        }
        var $form = $textarea.closest('form');
        $textarea.summernote({
        height: 250,
        });

            // pull-left class messes up the post layout OPW 769721
            $form.find('.note-editable').find('img.pull-left').removeClass('pull-left');
            $form.on('click', 'button, .a-submit', function () {
                $textarea.html($form.find('.note-editable').code());
            });
    });
    });

});

