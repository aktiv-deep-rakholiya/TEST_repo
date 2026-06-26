/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { browser } from "@web/core/browser/browser";
import { FsmTaskCalendarModel } from "@industry_fsm/views/fsm_task_calendar/fsm_calendar_model";
import { intersection } from "@web/core/utils/arrays";

const STORAGE_KEY = "fsm_calendar_assignee_filter_state";

patch(FsmTaskCalendarModel.prototype, {
    setup() {
        super.setup(...arguments);
        this.filterStorageKey = STORAGE_KEY;
    },

    _saveFilterState() {
        try {
            const snapshot = {};

            for (const [sectionName, section] of Object.entries(
                this.data.filterSections || {}
            )) {
                snapshot[sectionName] = Object.fromEntries(
                    section.filters.map((filter) => [
                        filter.value,
                        filter.active,
                    ])
                );
            }

            browser.localStorage.setItem(
                this.filterStorageKey,
                JSON.stringify(snapshot)
            );
        } catch (error) {
            console.warn("FSM: could not persist filter state", error);
        }
    },

    _loadFilterState() {
        try {
            const raw = browser.localStorage.getItem(this.filterStorageKey);
            return raw ? JSON.parse(raw) : null;
        } catch {
            return null;
        }
    },

    async updateFilters(fieldName, filters, active) {
        filters.forEach((filter) => {
            filter.active = active;
        });

        this._saveFilterState();

        await super.updateFilters(...arguments);
    },

    async loadDynamicFilters(data, dynamicFiltersInfo) {
        const sections = await super.loadDynamicFilters(...arguments);
        const savedState = this._loadFilterState();

        for (const [sectionName, section] of Object.entries(sections)) {
            const sectionState = savedState?.[sectionName];

            for (const filter of section.filters) {
                filter.active =
                    sectionState?.[filter.value] !== undefined
                        ? sectionState[filter.value]
                        : false;
            }
        }

        return sections;
    },

    async loadRecords(data) {
        const records = await super.loadRecords(data);

        this._cachedRecords = { ...records };

        return records;
    },

    async updateData(data) {
        await super.updateData(data);

        data.records = { ...this._cachedRecords };

        const filterSections = data.filterSections || {};

        for (const [fieldName, section] of Object.entries(filterSections)) {
            if (this.meta.filtersInfo[fieldName]?.writeResModel) {
                continue;
            }

            const activeFilters = section.filters.filter(
                (filter) => filter.active
            );

            if (!activeFilters.length) {
                continue;
            }

            const fieldMeta = this.meta.fields[fieldName];

            if (!fieldMeta) {
                continue;
            }

            const hiddenValues = new Set(
                section.filters
                    .filter((filter) => !filter.active)
                    .map((filter) => filter.value)
            );

            for (const [recordId, record] of Object.entries(data.records)) {
                const rawValue = record.rawRecord[fieldName];

                let shouldRemove = false;

                if (
                    fieldMeta.type === "many2many" ||
                    fieldMeta.type === "one2many"
                ) {
                    if (!rawValue?.length) {
                        shouldRemove = true;
                    } else {
                        const hiddenMatches = intersection(
                            rawValue,
                            [...hiddenValues]
                        );
                        shouldRemove =
                            hiddenMatches.length === rawValue.length;
                    }
                } else {
                    const value = Array.isArray(rawValue)
                        ? rawValue[0]
                        : rawValue;

                    shouldRemove =
                        !value || hiddenValues.has(value);
                }

                if (shouldRemove) {
                    delete data.records[recordId];
                }
            }
        }

        if (!this.aggregate) {
            return;
        }

        for (const [fieldName, section] of Object.entries(filterSections)) {
            const aggregatedValues = this.computeAggregatedValues(
                fieldName,
                data
            );

            for (const filter of section.filters) {
                filter.aggregatedValue =
                    aggregatedValues[filter.value] ?? 0;
            }
        }
    },
});