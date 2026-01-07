#!/bin/bash
# Quick start script for Odoo Pharmacy POS

cd /opt/odoo/odoo
python3 odoo-bin \
    -d pharmacy_kenya \
    --db_host=localhost \
    --db_user=julius \
    --db_password=julius \
    --addons-path=/opt/odoo/odoo/addons,/opt/odoo/odoo/addons/custom \
    2>&1 | tee /tmp/odoo.log
