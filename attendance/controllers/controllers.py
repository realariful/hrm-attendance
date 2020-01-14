from addons.crm.models import crm_lead
from odoo import http, models, fields, api
from odoo.exceptions import AccessError, MissingError
from odoo import models, fields, api, exceptions, _, SUPERUSER_ID
from odoo.http import request
import logging
import json
from datetime import datetime

_logger = logging.getLogger(__name__)


class LeadContactController(http.Controller):

    @http.route('/lead_contact/save_contact_data', auth='public', methods=['POST'], csrf=False)
    
    
    def save_contact_data(self, **values):
        
        auth_key = request.httprequest.headers['key']
        _logger.info(auth_key)

        if auth_key == 'Q29uZG9za3lDUk06c2VjdXJpdHlrZXkxMjU5Nzg2MzUxMw ==':
            try:
                
                check_in_vals = values['check_in'].split(",")
                check_in_vals = [i.strip(' ').lstrip(' ').rstrip(' ') for i in check_in_vals]
                date_time_str = "{} {} {} {} {}".format(check_in_vals[0],check_in_vals[1],check_in_vals[2],check_in_vals[3],check_in_vals[4])
                datetime_object = datetime.strptime(date_time_str, '%Y %m %d %H %M')               

                vals = {
                'employee_id': values['id'],
                'check_in': datetime_object,
                }
                records = request.env['hr.attendance'].sudo().create(vals)                       
                #import pdb; pdb.set_trace()
                return 
            except (AccessError, MissingError):
                return {
                    'success': False,
                    'status': 'unauthorized',
                    'code': 422
                }

        else:
           
            return {
                'success': False,
                'status': 'unauthorized',
                'code': 401}