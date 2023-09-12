//odoo.define('discipline_edit_rule', function (require) {
//    var FormView = require('web.FormView');
//    FormView.include({
//     load_record: function() {
//      this._super.apply(this, arguments);
//      if (this.model === 'op.discipline') {
//          if (this.datarecord && (this.datarecord.state === 'state')) {
//            this.$buttons.find('.o_form_button_edit').css({'display':'none'});
//          }
//          else {
//            this.$buttons.find('.o_form_button_edit').css({'display':''});
//          }
//       }
//    });
//});

//odoo.define('discipline_edit_rule', function(require) {
//    "use strict";
//
//    var KanbanController = require("web.KanbanController");
//    var ListController = require("web.ListController");
//
//    var includeDict = {
//        renderButtons: function () {
//            this._super.apply(this, arguments);
//                if (this.model === 'op.discipline') {
//                      if (this.datarecord && (this.datarecord.state === 'state')) {
//                        this.$buttons.find('.o_form_button_edit').css({'display':'none'});
//                      }
//                       else {
//                        this.$buttons.find('.o_form_button_edit').css({'display':''});
//                      }
//             }
//    };
//
//    KanbanController.include(includeDict);
//    ListController.include(includeDict);
//});