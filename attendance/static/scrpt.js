// odoo.define('custom_project.web_export_view', function (require) {

//     "use strict";
//     var core = require('web.core');
//     var ListView = require('web.ListView');
//     var ListController = require("web.ListController");

//     var includeDict = {
//         renderButtons: function () {
//             this._super.apply(this, arguments);
//             if (this.modelName === "mir_evl.attendance") {
//                 var your_btn = this.$buttons.find('button.o_button_help')
//                 your_btn.on('click', this.proxy('o_button_help'))
//             }
//         },
//         o_button_help: function () {
//         }
//     };
//     ListController.include(includeDict);
// });