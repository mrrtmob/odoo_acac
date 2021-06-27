odoo.define('openeducat_student_attendance_enterprise.student_kanban_view_handler', function(require) {
"use strict";

var KanbanRecord = require('web.KanbanRecord');

KanbanRecord.include({
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     * @private
     */
    _openRecord: function () {
        if (this.modelName === 'op.student' && this.$el.parents('.o_op_student_attendance_kanban').length) {
                                            // needed to diffentiate : sign in kanban view of students <-> standard student kanban view
            var action = {
                type: 'ir.actions.client',
                name: 'Confirm',
                tag: 'student_attendance_kiosk_confirm',
                student_id: this.record.id.raw_value,
                student_name: this.record.name.raw_value,
            };
            this.do_action(action);
        } else {
            this._super.apply(this, arguments);
        }
    }
});

});
