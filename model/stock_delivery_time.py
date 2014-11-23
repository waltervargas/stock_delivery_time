# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Stock Report Delivery Time                                                #
#   Copyright (C) 2014 Walter Vargas                                          #
#   Author :                                                                  #
#           Walter Vargas <walter@exds.net>                                   #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from openerp.osv import fields, osv
from openerp import tools

class stock_delivery_time(osv.osv):
    _name = 'stock.delivery.time'
    _description = 'Stock report/view for delivery time'
    _auto = False
    _columns = {
        'datediff': fields.char('Delivery Time (days)', readonly=True),
        'date': fields.date('Creation Date', readonly=True),
        'date_done': fields.date('Date of Transfer', readonly=True),
        'name': fields.char('Reference', readonly=True),
        'origin': fields.char(
            'Source Document',
            size=64,
            readonly=True,
            help="Reference of the document"
            ),
        }
    _order = 'datediff desc'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'stock.delivery.time')
        cr.execute("""
            CREATE OR REPLACE FUNCTION DateDiff (units VARCHAR(30), start_t TIMESTAMP, end_t TIMESTAMP) 
                 RETURNS INT AS $$
               DECLARE
                 diff_interval INTERVAL; 
                 diff INT = 0;
                 years_diff INT = 0;
               BEGIN
                 IF units IN ('yy', 'yyyy', 'year', 'mm', 'm', 'month') THEN
                   years_diff = DATE_PART('year', end_t) - DATE_PART('year', start_t);
             
                   IF units IN ('yy', 'yyyy', 'year') THEN
                     -- SQL Server does not count full years passed (only difference between year parts)
                     RETURN years_diff;
                   ELSE
                     -- If end month is less than start month it will subtracted
                     RETURN years_diff * 12 + (DATE_PART('month', end_t) - DATE_PART('month', start_t)); 
                   END IF;
                 END IF;
             
                 -- Minus operator returns interval 'DDD days HH:MI:SS'  
                 diff_interval = end_t - start_t;
             
                 diff = diff + DATE_PART('day', diff_interval);
             
                 IF units IN ('wk', 'ww', 'week') THEN
                   diff = diff/7;
                   RETURN diff;
                 END IF;
             
                 IF units IN ('dd', 'd', 'day') THEN
                   RETURN diff;
                 END IF;
             
                 diff = diff * 24 + DATE_PART('hour', diff_interval); 
             
                 IF units IN ('hh', 'hour') THEN
                    RETURN diff;
                 END IF;
             
                 diff = diff * 60 + DATE_PART('minute', diff_interval);
             
                 IF units IN ('mi', 'n', 'minute') THEN
                    RETURN diff;
                 END IF;
             
                 diff = diff * 60 + DATE_PART('second', diff_interval);
             
                 RETURN diff;
               END;
               $$ LANGUAGE plpgsql;""")

        cr.execute("""
          CREATE OR REPLACE VIEW stock_delivery_time AS (
           SELECT id, DATEDIFF('day', date, date_done), 
         	      date,
	              date_done,
                  name,
                  origin FROM stock_picking WHERE state = 'done'
           )
        """)

stock_delivery_time()
