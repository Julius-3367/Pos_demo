/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { useState } from "@odoo/owl";

export class BatchSelectionPopup extends AbstractAwaitablePopup {
    static template = "pos_demo.BatchSelectionPopup";

    setup() {
        super.setup();
        const batches = this.props.batches || [];
        
        // Sort batches by expiry date (FEFO)
        const sortedBatches = batches.sort((a, b) => {
            if (!a.expiry_date) return 1;
            if (!b.expiry_date) return -1;
            return new Date(a.expiry_date) - new Date(b.expiry_date);
        });

        this.state = useState({
            selectedBatch: sortedBatches[0] || null,
            batches: sortedBatches,
        });
    }

    selectBatch(batch) {
        // Check if batch is expired
        if (batch.is_expired) {
            this.showPopup('ErrorPopup', {
                title: _t('Expired Batch'),
                body: _t('This batch has expired and cannot be dispensed'),
            });
            return;
        }
        this.state.selectedBatch = batch;
    }

    getDaysToExpiry(expiryDate) {
        if (!expiryDate) return null;
        const today = new Date();
        const expiry = new Date(expiryDate);
        const diffTime = expiry - today;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays;
    }

    getExpiryClass(batch) {
        if (batch.is_expired) return 'text-danger';
        if (batch.expiry_alert) return 'text-warning';
        return '';
    }

    confirm() {
        if (this.state.selectedBatch) {
            this.props.resolve({ confirmed: true, payload: this.state.selectedBatch });
        } else {
            this.showPopup('ErrorPopup', {
                title: _t('No Batch Selected'),
                body: _t('Please select a batch/lot'),
            });
        }
    }

    cancel() {
        this.props.resolve({ confirmed: false });
    }
}
