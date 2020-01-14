import datetime
import pdb
from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
import time
import logging
from datetime import date, timedelta, datetime
import math


import datetime
import calendar
path_to_lib =  "/home/hisham/work/12_community/mir-admin/requisition/libraray/zk_library"

date = "03 02 2019"

# print(findDay(date))

def findDay(date):
    born = datetime.datetime.strptime(date, "%d %m %Y").weekday()
    return calendar.day_name[born]

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    from_date = fields.Date(string='From Date', help='From Date')
    date_to = fields.Date(string='Date To', help='Date To')
    ip_addr = fields.Char(string='Ip Address')
    port = fields.Char(string='Port Configuration')
    
    

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            from_date=self.env['ir.config_parameter'].sudo().get_param(
                'evl_attendance.from_date'),
            date_to=self.env['ir.config_parameter'].sudo().get_param(
                'evl_attendance.date_to'),

            ip_addr=self.env['ir.config_parameter'].sudo().get_param(
                'evl_attendance.ip_addr'),
            
            port=self.env['ir.config_parameter'].sudo().get_param(
                'evl_attendance.port'),

        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('evl_attendance.from_date',
                                                         self.from_date)
        self.env['ir.config_parameter'].sudo().set_param('evl_attendance.date_to',
                                                         self.date_to),


        self.env['ir.config_parameter'].sudo().set_param('evl_attendance.ip_addr',
                                                         self.ip_addr)
        self.env['ir.config_parameter'].sudo().set_param('evl_attendance.port',
                                                         self.port)








    

class override_base(models.Model):
    _inherit = "hr.attendance"

    source = fields.Selection([
        ('state1', 'Device'),
        ('state2', 'Movement')

    ],default = 'state1', string='')


    @api.constrains("check_in", "check_out", "employee_id")
    def _check_validity(self):
        
        for attendance in self:
           
            # import pdb; pdb.set_trace()
            if self.check_out == False or self.check_in== False:
                pass
            else:
                if not (self.check_out.date() == self.check_in.date()):
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the Checkout Date and Checkin date is not in the same day") % {
                        'empl_name': attendance.employee_id.name,                    
                    })



        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env["hr.attendance"].search(
                [
                    ("employee_id", "=", attendance.employee_id.id),
                    ("check_in", "<=", attendance.check_in),
                    ("id", "!=", attendance.id),
                ],
                order="check_in desc",
                limit=1,
            )
            if (
                last_attendance_before_check_in
                and last_attendance_before_check_in.check_out
                and last_attendance_before_check_in.check_out > attendance.check_in
            ):
                pass

                # raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                #     'empl_name': attendance.employee_id.name,
                #     'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(attendance.check_in))),
                # })

            if not attendance.check_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env["hr.attendance"].search(
                    [
                        ("employee_id", "=", attendance.employee_id.id),
                        ("check_out", "=", False),
                        ("id", "!=", attendance.id),
                    ],
                    order="check_in desc",
                    limit=1,
                )
                if no_check_out_attendances:

                    pass

                    # import pdb; pdb.set_trace()
                    # raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                    #     'empl_name': attendance.employee_id.name,
                    #     'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(no_check_out_attendances.check_in))),
                    # })
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env["hr.attendance"].search(
                    [
                        ("employee_id", "=", attendance.employee_id.id),
                        ("check_in", "<", attendance.check_out),
                        ("id", "!=", attendance.id),
                    ],
                    order="check_in desc",
                    limit=1,
                )
                if (
                    last_attendance_before_check_out
                    and last_attendance_before_check_in
                    != last_attendance_before_check_out
                ):
                    pass

                    # raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                    #     'empl_name': attendance.employee_id.name,
                    #     'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(last_attendance_before_check_out.check_in))),
                    # })


class Custom(models.Model):
    _name = "evl.attendance"
    _inherit = "hr.attendance"

    # @api.model
    # def abc(self):
    #     from_date = self.env['ir.config_parameter'].search([('key', '=', 'evl_attendance.from_date')]).value  
    #     to_date = self.env['ir.config_parameter'].search([('key', '=', 'evl_attendance.date_to')]).value

    early_leave_time = fields.Float(string="Early Leave", compute="_compute_early_time", store=True)
    late_time_daily = fields.Float(string="Late Time", compute="_compute_late_time", store=True)
    
    
    validity = fields.Selection([
        ('state0', 'draft'),        
        ('state1', 'Valid'),
        ('state2', 'Invalid')

    ],default = '', string='')
    
    
    bool_late = fields.Boolean(compute="_compute_late",store=True)
    bool_early = fields.Boolean(compute="_compute_early",store=True)
    source = fields.Selection([
        ('state1', 'Device'),
        ('state2', 'Movement')

    ],default = 'state1', string='')

    @api.depends("late_time_daily")
    def _compute_late(self):
        if self.late_time_daily > 0:
            self.bool_late = True
        else:
            self.bool_late = False

    @api.depends("late_time_daily")
    def _compute_early(self):
        if self.early_leave_time > 0:
            self.bool_early = True
        else:
            self.bool_early = False  

    # early_leave_time = fields.Char(string="Early Leave", compute="_compute_early_time", store=True)
    # late_time_daily = fields.Char(string="Late Time", compute="_compute_late_time", store=True)
    def update_in_device(self):
        import sys
        sys.path.append(path_to_lib)       
        from zk import ZK,const
        ip_address = self.env['ir.config_parameter'].search([('key', '=', 'evl_attendance.ip_addr')]).value
        port_number = self.env['ir.config_parameter'].search([('key', '=', 'evl_attendance.port')]).value
        zk = ZK(ip_address, port=int(port_number))
        conn = zk.connect()

        users = conn.get_users()
        devExistingUsers = [i.name for i in users]
        new_users_to_be_updated = self.env['hr.employee'].search([('name','not in',devExistingUsers)])
        # import pdb; pdb.set_trace()

        for users in new_users_to_be_updated:
            if users.identification_id:
                # import pdb; pdb.set_trace()
                try:
                    conn.set_user(name=str(users.name), privilege=const.USER_DEFAULT, password='12345678', user_id=users.identification_id)
                except Exception as e:
                    print ("Process terminate : {}".format(e))








    # def pull_from_device(self):
    #     print("--------------")
    #     import sys
    #     sys.path.append(path_to_lib)
    #     from zk import ZK
    #     from datetime import datetime, timedelta 
    #     ip_address = self.env['ir.config_parameter'].search([('key', '=', 'evl_attendance.ip_addr')]).value
    #     port_number = self.env['ir.config_parameter'].search([('key', '=', 'evl_attendance.port')]).value
    #     zk = ZK(ip_address, port=int(port_number))
    #     conn = zk.connect()
    #     attendances =  conn.get_attendance()

    #     for recs in attendances:
    #         if self.env['hr.employee'].search([('identification_id','=',recs.user_id)]):

    #             vals = {
    #                 'employee_id': self.env['hr.employee'].search([('identification_id','=',recs.user_id)]).id,
    #                 'check_in': recs.timestamp -timedelta(hours=6, minutes=0),
                    
    #                 }

    #             if not self.env['hr.attendance'].search([('employee_id','=',vals['employee_id']),('check_in','=',vals['check_in'])]):                
    #                 records = self.env['hr.attendance'].sudo().create(vals)
    #             else:
    #                 pass

        
        


    def cr_method(self):

        datas = self.env["hr.attendance"].search([])
        employee_list = []
        for recs in datas:
            if recs.employee_id not in employee_list:
                employee_list.append(recs.employee_id)

        for person in employee_list:
            records_a = datas.filtered(lambda r: r.employee_id.id == person.id)
            # import pdb; pdb.set_trace()
            date_a = []
            for items in records_a:
                
                if items.check_in.date() not in date_a:
                    date_a.append(items.check_in.date())
            
            for items_a in date_a:
                # fil_rec_in = datas.filtered(lambda r: r.check_in.date() == items_a and r.employee_id.id == person.id).sorted(key=lambda c: c.check_in)
                filtered_recs = datas.filtered(lambda r: r.check_in.date() == items_a and r.employee_id.id == person.id)
                
                sorted_min_checkin = filtered_recs.sorted(key=lambda c: c.check_in)[0]
                sorted_max_checkin = filtered_recs.sorted(key=lambda c: c.check_in)[-1]
                
                var = filtered_recs.filtered(lambda r: r.check_out != False).sorted(key=lambda c: c.check_out)

                if len(var) > 0 :
                    sorted_max_checkout = var[-1]
                    if sorted_max_checkout.check_out.time() > sorted_max_checkin.check_in.time():
                        final_check_out = sorted_max_checkout.check_out
                    else:
                        final_check_out = sorted_max_checkin.check_in
                    
                else:
                    final_check_out = sorted_max_checkin.check_in

                 
               
                # #########
                # finding CheckIn(Minimum)and Checkout(maximum) from existing model
                # #########################################################>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>done
                               
                search_if_existing =  self.env['evl.attendance'].search([]).filtered(lambda r: r.check_in.date() == sorted_min_checkin.check_in.date() and r.employee_id.id == person.id)

                if search_if_existing:
                    # import pdb; pdb.set_trace()
                    if search_if_existing.check_in.time() != sorted_min_checkin.check_in.time():
                        search_if_existing.update({"check_in": sorted_min_checkin.check_in})
                    # import pdb; pdb.set_trace()
                    if search_if_existing.check_out.time() != final_check_out.time():
                        search_if_existing.update({"check_out": final_check_out})                    
                else:
                    self.create(
                        {
                            "employee_id": person.id ,
                            "check_in": sorted_min_checkin.check_in,
                            "check_out": final_check_out,
                        }
                    )

                #import pdb; pdb.set_trace()
                
        for records in self.env['evl.attendance'].search([]):
            #For odoo11
            #valid_day_of_week = [int(i.dayofweek) for i in records.employee_id.contract_id.resource_calendar_id.attendance_ids]
            #For Odoo13
            valid_day_of_week = [int(i.dayofweek) for i in records.employee_id.resource_calendar_id.attendance_ids]
            	
            global_leaves = []
            #For Odoo11
            #for gleaves in records.employee_id.contract_id.resource_calendar_id.global_leave_ids:
            for gleaves in records.employee_id.resource_calendar_id.global_leave_ids:
               

                _from =(gleaves.date_from + timedelta(hours=6)).date()
                _to = (gleaves.date_to + timedelta(hours=6)).date()

                

                if _from != _to:
                    delta = _to - _from 
                    for i in range(delta.days + 1):
                        global_leaves.append(_from + timedelta(days=i))
                else:
                    global_leaves.append(_from)
                    global_leaves.append(_to)

            for leaves in self.env['resource.calendar.leaves'].search([('resource_id','=',records.employee_id.id)]):
                _from =(leaves.date_from + timedelta(hours=6)).date()
                _to = (leaves.date_to + timedelta(hours=6)).date()

                

                if _from != _to:
                    delta = _to - _from 
                    for i in range(delta.days + 1):
                        global_leaves.append(_from + timedelta(days=i))
                else:
                    global_leaves.append(_from)
                    global_leaves.append(_to)

            # import pdb; pdb.set_trace()


            if records.check_in.weekday() in valid_day_of_week:
                records.validity = 'state1'
            else:
                records.validity = 'state2'

            if records.check_in.date() in global_leaves:
                    records.validity = 'state2'
           



    @api.depends("check_in", "check_out")
    def _compute_late_time(self):
        select = {'Monday':0,'Tuesday':1,'Wednesday':2,'Thursday':3,'Friday':4,'Saturday':5,'Sunday':6}
        date = (str(self.check_in.day)+ " " + str(self.check_in.month)+ " " + str(self.check_in.year))
        day_of_week = str(select[findDay(date)])
        # import pdb; pdb.set_trace()

        for x in self.employee_id.resource_calendar_id.attendance_ids.filtered(lambda r: r.dayofweek == day_of_week):
            # import pdb; pdb.set_trace()            
            emp_check_in_hour = self.check_in.hour + 6
            emp_check_in_minute = round(self.check_in.minute/60,2)
            emp_check_in = emp_check_in_hour + emp_check_in_minute

            if emp_check_in > x.hour_from:
                late_calc = math.modf(round(emp_check_in - x.hour_from,2))
                
                self.late_time_daily = late_calc[1] + late_calc[0]

            else:
                self.late_time_daily = 0
                       
           
            

    @api.depends("check_in", "check_out")
    def _compute_early_time(self):
        select = {'Monday':0,'Tuesday':1,'Wednesday':2,'Thursday':3,'Friday':4,'Saturday':5,'Sunday':6}
        date = (str(self.check_out.day)+ " " + str(self.check_out.month)+ " " + str(self.check_out.year))
        day_of_week = str(select[findDay(date)])
        # self.early_leave_time = 1.5
        # return
        # import pdb; pdb.set_trace()

        for x in self.employee_id.resource_calendar_id.attendance_ids.filtered(lambda r: r.dayofweek == day_of_week):            
            emp_check_out_hour = self.check_out.hour + 6
            emp_check_out_minute = round(self.check_out.minute/60,2)
            emp_check_out = emp_check_out_hour + emp_check_out_minute
            
            # import pdb; pdb.set_trace()
            if emp_check_out < x.hour_to:
                late_calc = math.modf(round(x.hour_to - emp_check_out,2))

                # import pdb; pdb.set_trace()  

                if late_calc[1] != 0 :                                 
                    self.early_leave_time = late_calc[1] + late_calc[0]
                else:                                
                    self.early_leave_time = late_calc[0]
            else:
                self.early_leave_time = 0


            #############>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   type genetic  > char  00h00m
            # if emp_check_out < x.hour_to:
            #     late_calc = math.modf(round(x.hour_to - emp_check_out,2))
            #     if late_calc[1] != 0 :
            #         late_calc_h = int(late_calc[1])
            #         late_calc_m = int(late_calc[0]*60)                    
            #         self.early_leave_time = str(late_calc_h)+'h' + " " + str(late_calc_m)+'m'
            #     else:
            #         late_calc_m = int(late_calc[0]*60)
            #         self.early_leave_time = str(late_calc_m)+'m'
            # else:
            #     self.early_leave_time = "0:0"
            

    @api.constrains("check_in", "check_out", "employee_id")
    def _check_validity(self):        
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env["hr.attendance"].search(
                [
                    ("employee_id", "=", attendance.employee_id.id),
                    ("check_in", "<=", attendance.check_in),
                    ("id", "!=", attendance.id),
                ],
                order="check_in desc",
                limit=1,
            )
            if (
                last_attendance_before_check_in
                and last_attendance_before_check_in.check_out
                and last_attendance_before_check_in.check_out > attendance.check_in
            ):
                pass
               
            if not attendance.check_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env["hr.attendance"].search(
                    [
                        ("employee_id", "=", attendance.employee_id.id),
                        ("check_out", "=", False),
                        ("id", "!=", attendance.id),
                    ],
                    order="check_in desc",
                    limit=1,
                )
                if no_check_out_attendances:

                    pass
            else:                
                last_attendance_before_check_out = self.env["hr.attendance"].search(
                    [
                        ("employee_id", "=", attendance.employee_id.id),
                        ("check_in", "<", attendance.check_out),
                        ("id", "!=", attendance.id),
                    ],
                    order="check_in desc",
                    limit=1,
                )
                if (
                    last_attendance_before_check_out
                    and last_attendance_before_check_in
                    != last_attendance_before_check_out
                ):
                    pass