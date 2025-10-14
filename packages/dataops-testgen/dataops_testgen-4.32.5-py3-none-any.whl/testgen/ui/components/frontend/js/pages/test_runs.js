/**
 * @import { ProjectSummary } from '../types.js';
 * @import { SelectOption } from '../components/select.js';
 * 
 * @typedef TestRun
 * @type {object}
 * @property {string} test_run_id
 * @property {number} test_starttime
 * @property {number} test_endtime
 * @property {string} table_groups_name
 * @property {string} test_suite
 * @property {'Running'|'Complete'|'Error'|'Cancelled'} status
 * @property {string} log_message
 * @property {string} process_id
 * @property {number} test_ct
 * @property {number} passed_ct
 * @property {number} warning_ct
 * @property {number} failed_ct
 * @property {number} error_ct
 * @property {number} log_ct
 * @property {number} dismissed_ct
 * @property {string} dq_score_testing
 *
 * @typedef Permissions
 * @type {object}
 * @property {boolean} can_edit
 *
 * @typedef Properties
 * @type {object}
 * @property {ProjectSummary} project_summary
 * @property {TestRun[]} test_runs
 * @property {SelectOption[]} table_group_options
 * @property {SelectOption[]} test_suite_options
 * @property {Permissions} permissions
 */
import van from '../van.min.js';
import { Tooltip } from '../components/tooltip.js';
import { SummaryBar } from '../components/summary_bar.js';
import { Link } from '../components/link.js';
import { Button } from '../components/button.js';
import { Streamlit } from '../streamlit.js';
import { emitEvent, getValue, loadStylesheet, resizeFrameHeightToElement, resizeFrameHeightOnDOMChange } from '../utils.js';
import { formatTimestamp, formatDuration } from '../display_utils.js';
import { Checkbox } from '../components/checkbox.js';
import { Select } from '../components/select.js';
import { Paginator } from '../components/paginator.js';
import { EMPTY_STATE_MESSAGE, EmptyState } from '../components/empty_state.js';

const { div, i, span, strong } = van.tags;
const PAGE_SIZE = 100;
const SCROLL_CONTAINER = window.top.document.querySelector('.stMain');

const TestRuns = (/** @type Properties */ props) => {
    loadStylesheet('testRuns', stylesheet);
    Streamlit.setFrameHeight(1);
    window.testgen.isPage = true;

    const columns = ['5%', '28%', '17%', '40%', '10%'];
    const userCanEdit = getValue(props.permissions)?.can_edit ?? false;

    const pageIndex = van.state(0);
    const testRuns = van.derive(() => {
        pageIndex.val = 0;
        return getValue(props.test_runs);
    });
    const paginatedRuns = van.derive(() => testRuns.val.slice(PAGE_SIZE * pageIndex.val, PAGE_SIZE * (pageIndex.val + 1)));

    const selectedRuns = {};
    const initializeSelectedStates = (items) => {
        for (const testRun of items) {
            if (selectedRuns[testRun.test_run_id] == undefined) {
                selectedRuns[testRun.test_run_id] = van.state(false);
            }
        }
    };
    initializeSelectedStates(testRuns.val);
    van.derive(() => initializeSelectedStates(testRuns.val));

    const wrapperId = 'test-runs-list-wrapper';
    resizeFrameHeightToElement(wrapperId);
    resizeFrameHeightOnDOMChange(wrapperId);

    return div(
        { id: wrapperId },
        () => {
            const projectSummary = getValue(props.project_summary);
            return projectSummary.test_run_count > 0
            ? div(
                { class: 'tg-test-runs' },
                Toolbar(props, userCanEdit),
                () => testRuns.val.length
                ? div(
                    div(
                        { class: 'table' },
                        () => {
                            const selectedItems = testRuns.val.filter(i => selectedRuns[i.test_run_id]?.val ?? false);
                            const someRunSelected = selectedItems.length > 0;
                            const tooltipText = !someRunSelected ? 'No runs selected' : undefined;

                            if (!userCanEdit) {
                                return '';
                            }

                            return div(
                                { class: 'flex-row fx-justify-content-flex-end pb-2' },
                                someRunSelected ? strong({ class: 'mr-1' }, selectedItems.length) : '',
                                someRunSelected ? span({ class: 'mr-4' }, 'runs selected') : '',
                                Button({
                                    type: 'stroked',
                                    icon: 'delete',
                                    label: 'Delete Runs',
                                    tooltip: tooltipText,
                                    tooltipPosition: 'bottom-left',
                                    disabled: !someRunSelected,
                                    width: 'auto',
                                    onclick: () => emitEvent('RunsDeleted', { payload: selectedItems.map(i => i.test_run_id) }),
                                }),
                            );
                        },
                        div(
                            { class: 'table-header flex-row' },
                            () => {
                                const items = testRuns.val;
                                const selectedItems = items.filter(i => selectedRuns[i.test_run_id]?.val ?? false);
                                const allSelected = selectedItems.length === items.length;
                                const partiallySelected = selectedItems.length > 0 && selectedItems.length < items.length;

                                if (!userCanEdit) {
                                    return '';
                                }

                                return span(
                                    { style: `flex: ${columns[0]}` },
                                    userCanEdit
                                        ? Checkbox({
                                            checked: allSelected,
                                            indeterminate: partiallySelected,
                                            onChange: (checked) => items.forEach(item => selectedRuns[item.test_run_id].val = checked),
                                            testId: 'select-all-test-run',
                                        })
                                        : '',
                                );
                            },
                            span(
                                { style: `flex: ${columns[1]}` },
                                'Start Time | Table Group | Test Suite',
                            ),
                            span(
                                { style: `flex: ${columns[2]}` },
                                'Status | Duration',
                            ),
                            span(
                                { style: `flex: ${columns[3]}` },
                                'Results Summary',
                            ),
                            span(
                                { style: `flex: ${columns[4]}` },
                                'Testing Score',
                            ),
                        ),
                        div(
                            paginatedRuns.val.map(item => TestRunItem(item, columns, selectedRuns[item.test_run_id], userCanEdit)),
                        ),
                    ),
                    Paginator({
                        pageIndex,
                        count: testRuns.val.length,
                        pageSize: PAGE_SIZE,
                        onChange: (newIndex) => {
                            if (newIndex !== pageIndex.val) {
                                pageIndex.val = newIndex;
                                SCROLL_CONTAINER.scrollTop = 0;
                            }
                        },
                    }),
                )
                : div(
                    { class: 'pt-7 text-secondary', style: 'text-align: center;' },
                    'No test runs found matching filters',
                ),
            )
            : ConditionalEmptyState(projectSummary, userCanEdit);
        }
    );
};

const Toolbar = (
    /** @type Properties */ props,
    /** @type boolean */ userCanEdit,
) => {
    return div(
        { class: 'flex-row fx-align-flex-end fx-justify-space-between mb-4 fx-gap-4' },
        div(
            { class: 'flex-row fx-gap-4' },
            () => Select({
                label: 'Table Group',
                value: getValue(props.table_group_options)?.find((op) => op.selected)?.value ?? null,
                options: getValue(props.table_group_options) ?? [],
                allowNull: true,
                style: 'font-size: 14px;',
                testId: 'table-group-filter',
                onChange: (value) => emitEvent('FilterApplied', { payload: { table_group_id: value } }),
            }),
            () => Select({
                label: 'Test Suite',
                value: getValue(props.test_suite_options)?.find((op) => op.selected)?.value ?? null,
                options: getValue(props.test_suite_options) ?? [],
                allowNull: true,
                style: 'font-size: 14px;',
                testId: 'test-suite-filter',
                onChange: (value) => emitEvent('FilterApplied', { payload: { test_suite_id: value } }),
            }),
        ),
        div(
            { class: 'flex-row fx-gap-4' },
            Button({
                icon: 'today',
                type: 'stroked',
                label: 'Test Run Schedules',
                tooltip: 'Manage when test suites should run',
                tooltipPosition: 'bottom',
                width: 'fit-content',
                style: 'background: var(--dk-card-background);',
                onclick: () => emitEvent('RunSchedulesClicked', {}),
            }),
            userCanEdit
                ? Button({
                    icon: 'play_arrow',
                    type: 'stroked',
                    label: 'Run Tests',
                    width: 'fit-content',
                    style: 'background: var(--dk-card-background);',
                    onclick: () => emitEvent('RunTestsClicked', {}),
                })
                : '',
            Button({
                type: 'icon',
                icon: 'refresh',
                tooltip: 'Refresh test runs list',
                tooltipPosition: 'left',
                style: 'border: var(--button-stroked-border); border-radius: 4px;',
                onclick: () => emitEvent('RefreshData', {}),
                testId: 'test-runs-refresh',
            }),
        ),
    );
};

const TestRunItem = (
    /** @type TestRun */ item,
    /** @type string[] */ columns,
    /** @type boolean */ selected,
    /** @type boolean */ userCanEdit,
) => {
    return div(
        { class: 'table-row flex-row' },
        userCanEdit
            ? div(
                { style: `flex: ${columns[0]}; font-size: 16px;` },
                Checkbox({
                    checked: selected,
                    onChange: (checked) => selected.val = checked,
                    testId: 'select-test-run',
                }),
            )
            : '',
        div(
            { style: `flex: ${columns[1]}` },
            Link({
                label: formatTimestamp(item.test_starttime),
                href: 'test-runs:results',
                params: { 'run_id': item.test_run_id },
                underline: true,
            }),
            div(
                { class: 'text-caption mt-1' },
                `${item.table_groups_name} > ${item.test_suite}`,
            ),
        ),
        div(
            { class: 'flex-row', style: `flex: ${columns[2]}` },
            div(
                TestRunStatus(item),
                div(
                    { class: 'text-caption mt-1' },
                    formatDuration(item.test_starttime, item.test_endtime),
                ),
            ),
            item.status === 'Running' && item.process_id && userCanEdit ? Button({
                type: 'stroked',
                label: 'Cancel Run',
                style: 'width: auto; height: 32px; color: var(--purple); margin-left: 16px;',
                onclick: () => emitEvent('RunCanceled', { payload: item }),
            }) : null,
        ),
        div(
            { class: 'pr-3', style: `flex: ${columns[3]}` },
            item.test_ct ? SummaryBar({
                items: [
                    { label: 'Passed', value: item.passed_ct, color: 'green' },
                    { label: 'Warning', value: item.warning_ct, color: 'yellow' },
                    { label: 'Failed', value: item.failed_ct, color: 'red' },
                    { label: 'Error', value: item.error_ct, color: 'brown' },
                    { label: 'Log', value: item.log_ct, color: 'blue' },
                    { label: 'Dismissed', value: item.dismissed_ct, color: 'grey' },
                ],
                height: 8,
                width: 350,
            }) : '--',
        ),
        div(
            { style: `flex: ${columns[4]}; font-size: 16px;` },
            item.test_ct && item.dq_score_testing
                ? item.dq_score_testing
                : '--',
        ),
    );
}

function TestRunStatus(/** @type TestRun */ item) {
    const attributeMap = {
        Running: { label: 'Running', color: 'blue' },
        Complete: { label: 'Completed', color: '' },
        Error: { label: 'Error', color: 'red' },
        Cancelled: { label: 'Canceled', color: 'purple' },
    };
    const attributes = attributeMap[item.status] || { label: 'Unknown', color: 'grey' };
    return span(
        {
            class: 'flex-row',
            style: `color: var(--${attributes.color});`,
        },
        attributes.label,
        () => {
            const tooltipError = van.state(false);
            return item.status === 'Error' && item.log_message ? i(
                {
                    class: 'material-symbols-rounded text-secondary ml-1',
                    style: 'position: relative; font-size: 16px;',
                    onmouseenter: () => tooltipError.val = true,
                    onmouseleave: () => tooltipError.val = false,
                },
                'info',
                Tooltip({ text: item.log_message, show: tooltipError }),
            ) : null;
        },
    );
}

const ConditionalEmptyState = (
    /** @type ProjectSummary */ projectSummary,
    /** @type boolean */ userCanEdit,
) => {
    let args = {
        message: EMPTY_STATE_MESSAGE.testExecution,
        button: Button({
            icon: 'play_arrow',
            type: 'stroked',
            color: 'primary',
            label: 'Run Tests',
            width: 'fit-content',
            style: 'margin: auto; background: var(--dk-card-background);',
            disabled: !userCanEdit,
            tooltip: userCanEdit ? null : DISABLED_ACTION_TEXT,
            tooltipPosition: 'bottom',
            onclick: () => emitEvent('RunTestsClicked', {}),
        }),
    };

    if (projectSummary.connection_count <= 0) {
        args = {
            message: EMPTY_STATE_MESSAGE.connection,
            link: {
                label: 'Go to Connections',
                href: 'connections',
                params: { project_code: projectSummary.project_code },
            },
        };
    } else if (projectSummary.table_group_count <= 0) {
        args = {
            message: EMPTY_STATE_MESSAGE.tableGroup,
            link: {
                label: 'Go to Table Groups',
                href: 'table-groups',
                params: { project_code: projectSummary.project_code, connection_id: projectSummary.default_connection_id },
            },
        };
    } else if (projectSummary.test_suite_count <= 0 || projectSummary.test_definition_count <= 0) {
        args = {
            message: EMPTY_STATE_MESSAGE.testSuite,
            link: {
                label: 'Go to Test Suites',
                href: 'test-suites',
                params: { project_code: projectSummary.project_code },
            },
        };
    }

    return EmptyState({
        icon: 'labs',
        label: 'No test runs yet',
        ...args,
    });
};

const stylesheet = new CSSStyleSheet();
stylesheet.replace(`
.tg-test-runs {
    min-height: 500px;
}
`);

export { TestRuns };
