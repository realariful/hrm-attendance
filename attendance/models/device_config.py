from odoo import models, fields, api, exceptions
import sys
import os
sys.path.insert(1,os.path.abspath("./pyzk"))
from zk import ZK, const
from datetime import datetime, timedelta 

class DeviceConfig(models.Model):
    _name = 'device.config'
    _description = 'Device Configuration'
    
    dev_ip = fields.Char(string='Eg 192.168.0.101', required=True)
    port_no = fields.Integer(string='Port No', required=True, default='4370')
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    location = fields.Char(string='Location', required=True)

    username = fields.Char(string='Username')
    password = fields.Char(string='Password')

    @api.model
    def create(self,values):
        record = super(DeviceConfig,self).create(values)
        print(record)
        from datetime import timedelta,datetime
        
        #.strftime('%Y-%m-%d 00:00:00')
        if record:

            vals = {
                'user_id': 1, 
                'interval_number': 1, 
                'interval_type': 'minutes',
                'active': True, 
                'nextcall': (datetime.now() + timedelta(minutes=1)),
                'numbercall': -1,
                'priority': 5,
                'state': 'code', 
                'type': 'ir.actions.server', 
                'sms_mass_keep_log': True,                 
                'code': 'model.fp_device_create_cron('+str(record.id)+')',
                'activity_date_deadline_range_type': 'days', 
                'activity_user_type': 'specific', 
                'activity_user_field_name': 'user_id', 
                'binding_model_id': False, 
                'binding_type': 'action', 
                'name': "Pull from Device-" +str(record.id), 
                'doall': False,
                'model_id': 346, 
                'crud_model_id': False,
                'link_field_id': False,
                'sms_template_id': False,
                'template_id': False, 
                'activity_type_id': False, 
                'activity_summary': False, 
                'activity_date_deadline_range': 0,
                'activity_user_id': False, 
                'activity_note': '<p><br></p>',
                'usage': 'ir_cron',
            }

            cronObj = self.env['ir.cron'].create(vals)
            if cronObj:
                pass
                #import pdb; pdb.set_trace()
            
            print(cronObj)
            return record

     



    def fp_device_fetch(self,dev_ip,port_no):      
        import sys
        from zk import ZK
        from datetime import datetime, timedelta 
        #devices = self.env['device.config'].search([])
        #for dev in devices:  
        print(dev_ip, port_no)
        zk = ZK(dev_ip, port=int(port_no))
        conn = zk.connect()
        attendances =  conn.get_attendance()


        for recs in attendances:
            
            if self.env['hr.employee'].search([('identification_id','=',recs.user_id)]):

                vals = {
                    'employee_id': self.env['hr.employee'].search([('identification_id','=',recs.user_id)]).id,
                    'check_in': recs.timestamp -timedelta(hours=6, minutes=0),                        
                    }                          
                vals['check_in'] = datetime.strftime(vals['check_in'], '%Y-%m-%d %H:%M:%S')
                #print(type(vals['check_in']))

                if not self.env['hr.attendance'].search([('employee_id','=',vals['employee_id']),('check_in','=',vals['check_in'])]):
                    print("No Match")                
                    records = self.env['hr.attendance'].sudo().create(vals)
                    #self.env.cr.commit()
                    print(records)
                else:
                    pass


    #Create a new cron for new device
    def fp_device_create_cron(self,id):
        print("Your code run")
        import pdb; pdb.set_trace()

        print(id)
        dev = self.env['device.config'].search([('id','=',id)])
        print(dev.dev_ip, dev.port)


        zk = ZK(dev.dev_ip, port=int(dev.port_no))
        conn = zk.connect()
        attendances =  conn.get_attendance()


        for recs in attendances:
            
            if self.env['hr.employee'].search([('identification_id','=',recs.user_id)]):

                vals = {
                    'employee_id': self.env['hr.employee'].search([('identification_id','=',recs.user_id)]).id,
                    'check_in': recs.timestamp -timedelta(hours=6, minutes=0),                        
                    }                          
                vals['check_in'] = datetime.strftime(vals['check_in'], '%Y-%m-%d %H:%M:%S')
                #print(type(vals['check_in']))

                if not self.env['hr.attendance'].search([('employee_id','=',vals['employee_id']),('check_in','=',vals['check_in'])]):
                    print("No Match")                
                    records = self.env['hr.attendance'].sudo().create(vals)
                    #self.env.cr.commit()
                    print(records)
                else:
                    pass


    def fp_device_fetch_data(self):      

        devices = self.env['device.config'].search([])
        for dev in devices:  
            print(dev.dev_ip, dev.port_no)
            zk = ZK(dev.dev_ip, port=int(dev.port_no))
            conn = zk.connect()
            attendances =  conn.get_attendance()


            for recs in attendances:
                
                if self.env['hr.employee'].search([('identification_id','=',recs.user_id)]):

                    vals = {
                        'employee_id': self.env['hr.employee'].search([('identification_id','=',recs.user_id)]).id,
                        'check_in': recs.timestamp -timedelta(hours=6, minutes=0),                        
                        }                          
                    vals['check_in'] = datetime.strftime(vals['check_in'], '%Y-%m-%d %H:%M:%S')
                    #print(type(vals['check_in']))

                    if not self.env['hr.attendance'].search([('employee_id','=',vals['employee_id']),('check_in','=',vals['check_in'])]):
                        print("No Match")                
                        records = self.env['hr.attendance'].sudo().create(vals)
                        #self.env.cr.commit()
                        print(records)
                    else:
                        pass
    