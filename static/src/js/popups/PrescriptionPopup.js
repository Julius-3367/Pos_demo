/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { useState } from "@odoo/owl";

export class PrescriptionPopup extends AbstractAwaitablePopup {
    static template = "pos_demo.PrescriptionPopup";

    setup() {
        super.setup();
        this.state = useState({
            searchTerm: '',
            selectedPrescription: null,
            prescriptions: this.props.prescriptions || [],
            filteredPrescriptions: this.props.prescriptions || [],
        });
    }

    onSearchInput(event) {
        const term = event.target.value.toLowerCase();
        this.state.searchTerm = term;
        this.state.filteredPrescriptions = this.state.prescriptions.filter(rx =>
            rx.name.toLowerCase().includes(term) ||
            rx.patient_id[1].toLowerCase().includes(term)
        );
    }

    selectPrescription(prescription) {
        this.state.selectedPrescription = prescription;
    }

    confirm() {
        if (this.state.selectedPrescription) {
            this.props.resolve({ confirmed: true, payload: this.state.selectedPrescription });
        } else {
            this.showPopup('ErrorPopup', {
                title: _t('No Prescription Selected'),
                body: _t('Please select a prescription'),
            });
        }
    }

    cancel() {
        this.props.resolve({ confirmed: false });
    }
}
