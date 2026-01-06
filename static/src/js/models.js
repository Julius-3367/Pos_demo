/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

// Extend POS Store for pharmacy functionality
patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        
        // Load pharmacy-specific data
        this.prescriptions = loadedData['pharmacy.prescription'] || [];
        this.insurance_providers = loadedData['insurance.provider'] || [];
        this.controlled_drugs = loadedData['product.product'].filter(
            p => p.is_controlled_substance
        );
    },

    // Check if product requires prescription
    requiresPrescription(product) {
        return product.requires_prescription || false;
    },

    // Check if product is expired
    isProductExpired(product, lot) {
        if (!lot || !lot.expiry_date) {
            return false;
        }
        const today = new Date();
        const expiryDate = new Date(lot.expiry_date);
        return expiryDate < today;
    },

    // Check if product is expiring soon
    isProductExpiringSoon(lot, days = 180) {
        if (!lot || !lot.expiry_date) {
            return false;
        }
        const today = new Date();
        const expiryDate = new Date(lot.expiry_date);
        const diffTime = expiryDate - today;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays > 0 && diffDays <= days;
    },

    // Get patient's recent purchases for interaction checking
    async getPatientHistory(patientId, days = 30) {
        try {
            const result = await this.env.services.rpc({
                route: '/pos_demo/get_patient_history',
                params: {
                    patient_id: patientId,
                    days: days
                }
            });
            return result.products || [];
        } catch (error) {
            console.error('Error fetching patient history:', error);
            return [];
        }
    },

    // Verify insurance eligibility
    async verifyInsurance(memberNumber, providerId) {
        try {
            const result = await this.env.services.rpc({
                route: '/pos_demo/verify_insurance',
                params: {
                    member_number: memberNumber,
                    provider_id: providerId
                }
            });
            return result;
        } catch (error) {
            console.error('Error verifying insurance:', error);
            return { error: 'Verification failed' };
        }
    }
});

// Extend Order model for pharmacy
patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
        this.prescription_id = this.prescription_id || null;
        this.insurance_provider_id = this.insurance_provider_id || null;
        this.insurance_member_number = this.insurance_member_number || null;
        this.patient_copay = this.patient_copay || 0;
        this.has_prescription_items = this.has_prescription_items || false;
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.prescription_id = this.prescription_id;
        json.insurance_provider_id = this.insurance_provider_id;
        json.insurance_member_number = this.insurance_member_number;
        json.patient_copay = this.patient_copay;
        json.has_prescription_items = this.has_prescription_items;
        return json;
    },

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.prescription_id = json.prescription_id;
        this.insurance_provider_id = json.insurance_provider_id;
        this.insurance_member_number = json.insurance_member_number;
        this.patient_copay = json.patient_copay || 0;
        this.has_prescription_items = json.has_prescription_items || false;
    },

    // Check if order contains prescription items
    checkPrescriptionItems() {
        const lines = this.get_orderlines();
        this.has_prescription_items = lines.some(line => 
            line.product.requires_prescription
        );
        return this.has_prescription_items;
    },

    // Check if order contains controlled substances
    hasControlledSubstances() {
        const lines = this.get_orderlines();
        return lines.some(line => line.product.is_controlled_substance);
    }
});
