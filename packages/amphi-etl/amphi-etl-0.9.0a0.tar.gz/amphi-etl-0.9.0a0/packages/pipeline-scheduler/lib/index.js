import { ICommandPalette, ReactWidget } from '@jupyterlab/apputils';
import { ServerConnection } from '@jupyterlab/services';
import { requestScheduler } from './handler';
import { IDocumentManager } from '@jupyterlab/docmanager';
import React, { useState, useEffect } from 'react';
import { CalendarOutlined, ClockCircleOutlined, DeleteOutlined, EditOutlined, PlayCircleOutlined, PlusOutlined, ReloadOutlined, ScheduleOutlined, FolderOpenOutlined } from '@ant-design/icons';
import { schedulerIcon } from './icons';
import { Button, DatePicker, Empty, Form, Input, InputNumber, List, Modal, Radio, Select, Space, Spin, Tag, Tooltip, message, ConfigProvider } from 'antd';
import { createStyles } from 'antd-style';
import dayjs from 'dayjs'; // Import dayjs and Dayjs type
import { showBrowseFileDialog } from './BrowseFileDialog'; /* NEW */
import { Notification } from '@jupyterlab/apputils';
function toHeaderRecord(h) {
    if (!h)
        return {};
    if (h instanceof Headers) {
        const obj = {};
        h.forEach((v, k) => (obj[k] = v));
        return obj;
    }
    if (Array.isArray(h))
        return Object.fromEntries(h);
    return { ...h };
}
/* ---------- API Client ---------- */
class SchedulerAPI {
    static async makeRequest(endpoint, init = {}) {
        const settings = ServerConnection.makeSettings();
        const urlPatterns = ['pipeline-scheduler'];
        let lastError = null;
        for (const baseEndpoint of urlPatterns) {
            try {
                // take body out first so we can re-type it safely
                const { body, ...rest } = init;
                const requestInit = { ...rest };
                // normalize headers to a plain object we can mutate
                const headers = toHeaderRecord(rest.headers);
                const method = (rest.method || 'GET').toUpperCase();
                if (method !== 'GET' && body != null) {
                    const isPlainObject = typeof body === 'object' &&
                        !(body instanceof FormData) &&
                        !(body instanceof URLSearchParams) &&
                        !(body instanceof ArrayBuffer) &&
                        !(body instanceof Blob);
                    if (isPlainObject) {
                        requestInit.body = JSON.stringify(body);
                        headers['Content-Type'] = headers['Content-Type'] || 'application/json';
                    }
                    else {
                        requestInit.body = body;
                    }
                }
                requestInit.headers = headers;
                const response = await requestScheduler(endpoint, requestInit);
                return response;
            }
            catch (error) {
                console.warn(`Failed to connect using ${baseEndpoint}:`, error);
                lastError = error instanceof Error ? error : new Error(String(error));
            }
        }
        throw lastError || new Error('Failed to connect to any API endpoint');
    }
    static listJobs() {
        return this.makeRequest('jobs');
    }
    static getJob(id) {
        return this.makeRequest(`jobs/${id}`);
    }
    static createJob(job) {
        return this.makeRequest('jobs', {
            method: 'POST',
            body: job // This will be properly serialized by makeRequest
        });
    }
    static deleteJob(id) {
        return this.makeRequest(`jobs/${id}`, {
            method: 'DELETE'
        });
    }
    static runJob(id) {
        // Server does not read a body here
        return this.makeRequest(`run/${id}`, { method: 'POST' });
    }
}
/* ---------- styles ---------- */
const useStyle = createStyles(({ token, css }) => ({
    root: css `
    display: flex;
    flex-direction: column;
    height: 100%;
    background: ${token.colorBgContainer};
    color: ${token.colorText};
  `,
    header: css `
    height: 52px;
    border-bottom: 1px solid ${token.colorBorder};
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 12px 0 16px;
  `,
    headerTitle: css `
    font-weight: 600;
    font-size: 15px;
  `,
    content: css `
    flex: 1;
    overflow: auto;
    padding: 16px;
  `,
    jobCard: css `
    margin-bottom: 12px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  `,
    jobMeta: css `
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    color: ${token.colorTextSecondary};
  `,
    jobMetaIcon: css `
    margin-right: 6px;
  `,
    actionsBar: css `
    padding: 12px 16px;
    border-top: 1px solid ${token.colorBorder};
    display: flex;
    justify-content: space-between;
  `
}));
/* ---------- Components ---------- */
const JobForm = ({ docManager, onSubmit, onCancel, initialValues }) => {
    const [form] = Form.useForm();
    const [scheduleType, setScheduleType] = useState((initialValues === null || initialValues === void 0 ? void 0 : initialValues.schedule_type) || 'date');
    const [dateType, setDateType] = useState((initialValues === null || initialValues === void 0 ? void 0 : initialValues.date_type) || 'once');
    useEffect(() => {
        if (initialValues) {
            form.setFieldsValue(initialValues);
            setScheduleType(initialValues.schedule_type || 'date');
            setDateType(initialValues.date_type || 'once');
        }
    }, [initialValues, form]);
    /* helper to launch the file-picker */
    const pickPipelinePath = async () => {
        try {
            const res = await showBrowseFileDialog(docManager, {
                extensions: ['.ampln', '.py'],
                includeDir: false
            });
            if (res.button.accept && res.value.length) {
                form.setFieldsValue({ pipeline_path: res.value[0].path });
            }
        }
        catch (err) {
            console.error('Browse file error:', err);
            message.error('Failed to open file chooser');
        }
    };
    return (React.createElement(ConfigProvider, { theme: {
            token: {
                colorPrimary: '#5F9B97',
            },
        } },
        React.createElement(Form, { form: form, layout: "vertical", onFinish: onSubmit, initialValues: { schedule_type: 'date', date_type: 'once', ...initialValues } },
            React.createElement(Form.Item, { name: "id", hidden: true },
                React.createElement(Input, null)),
            React.createElement(Form.Item, { style: { marginBottom: 16 }, name: "name", label: "Task Name", rules: [{ required: true, message: 'Please input a task name' }] },
                React.createElement(Input, { placeholder: "My Task Name" })),
            React.createElement(Form.Item, { style: { marginBottom: 16 }, label: "Pipeline Path", required: true },
                React.createElement(Space.Compact, { style: { width: '100%' } },
                    React.createElement(Form.Item, { name: "pipeline_path", noStyle: true, rules: [{ required: true, message: 'Please select a pipeline file' }] },
                        React.createElement(Input, { readOnly: true, placeholder: "Select a .ampln or .py file" })),
                    React.createElement(Button, { icon: React.createElement(FolderOpenOutlined, null), onClick: pickPipelinePath }))),
            React.createElement(Form.Item, { style: { marginBottom: 16 }, name: "schedule_type", label: "Schedule Type" },
                React.createElement(Radio.Group, { onChange: (e) => setScheduleType(e.target.value) },
                    React.createElement(Radio, { value: "date" }, "Date"),
                    React.createElement(Radio, { value: "interval" }, "Interval"),
                    React.createElement(Radio, { value: "cron" }, "Cron"))),
            scheduleType === 'date' && (React.createElement(React.Fragment, null,
                React.createElement(Form.Item, { style: { marginBottom: 16 }, name: "date_type", label: "Date Type" },
                    React.createElement(Select, { onChange: (value) => setDateType(value), style: { width: '100%' } },
                        React.createElement(Select.Option, { value: "once" }, "One-time"),
                        React.createElement(Select.Option, { value: "daily" }, "Daily"),
                        React.createElement(Select.Option, { value: "weekly" }, "Weekly"),
                        React.createElement(Select.Option, { value: "monthly" }, "Monthly"),
                        React.createElement(Select.Option, { value: "every_x_days" }, "Every X Days"))),
                dateType !== 'every_x_days' ? (React.createElement(Form.Item, { style: { marginBottom: 16 }, name: "run_date", label: dateType === 'once' ? 'Run Date & Time' : 'Start Date & Time', rules: [{ required: true, message: 'Please select a date and time' }] },
                    React.createElement(DatePicker, { showTime: true, style: { width: '100%' } }))) : (React.createElement(Form.Item, { style: { marginBottom: 16 }, name: "interval_days", label: "Interval (days)", rules: [{ required: true, message: 'Please input a number of days' }] },
                    React.createElement(InputNumber, { min: 1, style: { width: '100%' } }))))),
            scheduleType === 'interval' && (React.createElement(Form.Item, { style: { marginBottom: 16 }, name: "interval_seconds", label: "Interval (seconds)", rules: [{ required: true, message: 'Please input an interval' }] },
                React.createElement(InputNumber, { min: 1, style: { width: '100%' } }))),
            scheduleType === 'cron' && (React.createElement(Form.Item, { style: { marginBottom: 16 }, name: "cron_expression", label: "Cron Expression", rules: [{ required: true, message: 'Please input a cron expression' }] },
                React.createElement(Input, { placeholder: "*/5 * * * *" }))),
            React.createElement(Form.Item, null,
                React.createElement(Space, { style: { marginBottom: 16, width: '100%', justifyContent: 'flex-end' } },
                    React.createElement(Button, { onClick: onCancel }, "Cancel"),
                    React.createElement(Button, { type: "primary", htmlType: "submit" }, "Submit"))))));
};
/** getPythonCode – convert .ampln to Python */
const getPythonCode = async (path, commands, docManager) => {
    console.log('Loaded path:', path);
    // Ask for text; server may still return JSON for certain mimetypes
    const file = await docManager.services.contents.get(path, {
        content: true,
        format: 'text'
    });
    console.log('Loaded file:', file);
    if (file.content == null) {
        console.error('File content is empty or null:', path);
        throw new Error('Selected file is empty or could not be loaded');
    }
    if (path.endsWith('.ampln')) {
        try {
            const raw = file.content;
            const jsonString = typeof raw === 'string'
                ? raw
                : JSON.stringify(raw);
            // Many generators expect a string and will JSON.parse internally.
            const code = (await commands.execute('pipeline-editor:generate-code', {
                json: jsonString
            }));
            console.log('Generated Python code:', code);
            if (!code)
                throw new Error('Code generation failed');
            return code;
        }
        catch (err) {
            console.error('Error during code generation:', err);
            throw err;
        }
    }
    // .py and others: the server returns text, so just forward it
    return file.content;
};
const SchedulerPanel = ({ commands, docManager }) => {
    const { styles } = useStyle();
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [jobModalVisible, setJobModalVisible] = useState(false);
    const [currentJob, setCurrentJob] = useState(null);
    const fetchJobs = async () => {
        setLoading(true);
        try {
            const data = await SchedulerAPI.listJobs();
            setJobs(data.jobs || []);
        }
        catch (error) {
            console.error('Error fetching jobs:', error);
            Notification.error('Failed to fetch scheduled jobs');
        }
        finally {
            setLoading(false);
        }
    };
    useEffect(() => {
        fetchJobs();
        // Set up a refresh interval
        const intervalId = setInterval(fetchJobs, 30000); // Refresh every 30 seconds
        return () => clearInterval(intervalId);
    }, []);
    const handleCreateJob = () => {
        setCurrentJob(null);
        setJobModalVisible(true);
    };
    const handleEditJob = (job) => {
        // Need to transform the job data to form values
        const formValues = {
            id: job.id,
            name: job.name,
            pipeline_path: job.pipeline_path,
            schedule_type: job.schedule_type
        };
        if (job.schedule_type === 'date') {
            formValues.date_type = job.date_type || 'once';
            if (job.run_date) {
                formValues.run_date = dayjs(job.run_date);
            }
            if (job.date_type === 'every_x_days') {
                formValues.interval_days = job.interval_days;
            }
        }
        if (job.schedule_type === 'interval') {
            formValues.interval_seconds = job.interval_seconds;
        }
        if (job.schedule_type === 'cron') {
            formValues.cron_expression = job.cron_expression;
        }
        setCurrentJob(formValues);
        setJobModalVisible(true);
    };
    const handleDeleteJob = (jobId) => {
        const promise = SchedulerAPI.deleteJob(jobId);
        Notification.promise(promise, {
            pending: { message: 'Deleting job…' },
            success: { message: () => 'Job deleted successfully', options: { autoClose: 3000 } },
            error: {
                message: (err) => `Failed to delete job: ${err instanceof Error ? err.message : String(err)}`
            }
        });
        promise.then(fetchJobs).catch(console.error);
    };
    const handleRunJob = async (jobId) => {
        const job = jobs.find(j => j.id === jobId);
        if (!job)
            return;
        const pythonCode = await getPythonCode(job.pipeline_path, commands, docManager);
        const promise = SchedulerAPI.runJob(jobId).then(res => {
            var _a;
            if (!res.success)
                throw new Error(res.error || 'Execution failed');
            return (_a = res.output) !== null && _a !== void 0 ? _a : '';
        });
        Notification.promise(promise, {
            pending: { message: 'Running pipeline…' },
            success: { message: () => 'Pipeline executed successfully' },
            error: {
                message: (e) => `Pipeline execution failed: ${e instanceof Error ? e.message : String(e)}`
            }
        });
    };
    const handleFormSubmit = async (values) => {
        try {
            /* build payload for backend */
            const formData = {
                name: values.name,
                schedule_type: values.schedule_type,
                run_date: values.run_date ? values.run_date.toDate().toISOString() : undefined,
                interval_seconds: values.interval_seconds,
                cron_expression: values.cron_expression,
                pipeline_path: values.pipeline_path // ALWAYS send the original path
            };
            // Add date_type if schedule_type is 'date'
            if (values.schedule_type === 'date') {
                formData.date_type = values.date_type || 'once';
                if (values.date_type === 'every_x_days') {
                    formData.interval_days = values.interval_days;
                }
            }
            if (values.id)
                formData.id = values.id;
            /* .ampln → also send raw Python code */
            if (values.pipeline_path.endsWith('.ampln')) {
                formData.python_code = await getPythonCode(values.pipeline_path, commands, docManager);
            }
            await SchedulerAPI.createJob(formData);
            Notification.success('Job created successfully');
            setJobModalVisible(false);
            fetchJobs();
        }
        catch (error) {
            console.error('Error creating job:', error);
            Notification.error('Failed to create job');
        }
    };
    return (React.createElement(ConfigProvider, { theme: {
            token: {
                colorPrimary: '#5F9B97',
            },
        } },
        React.createElement("div", { className: styles.root },
            React.createElement("div", { className: styles.header },
                React.createElement(Space, null,
                    React.createElement(Button, { type: "primary", icon: React.createElement(PlusOutlined, null), onClick: handleCreateJob }, "Task"),
                    React.createElement(Button, { icon: React.createElement(ReloadOutlined, null), onClick: fetchJobs }))),
            React.createElement("div", { className: styles.content }, loading ? (React.createElement("div", { style: { textAlign: 'center', padding: '40px 0' } },
                React.createElement(Spin, { size: "large" }))) : jobs.length === 0 ? (React.createElement(Empty, { description: "No scheduled tasks yet", image: Empty.PRESENTED_IMAGE_SIMPLE })) : (React.createElement(List, { itemLayout: "vertical", dataSource: jobs, renderItem: job => {
                    const type = job.trigger.split('[')[0];
                    return (React.createElement(List.Item, { key: job.id, actions: [
                            React.createElement(Tooltip, { title: "Run now", key: "run" },
                                React.createElement(Button, { type: "text", icon: React.createElement(PlayCircleOutlined, null), onClick: () => handleRunJob(job.id) })),
                            React.createElement(Tooltip, { title: "Edit", key: "edit" },
                                React.createElement(Button, { type: "text", icon: React.createElement(EditOutlined, null), onClick: () => handleEditJob(job) })),
                            React.createElement(Tooltip, { title: "Delete", key: "delete" },
                                React.createElement(Button, { type: "text", danger: true, icon: React.createElement(DeleteOutlined, null), onClick: () => handleDeleteJob(job.id) }))
                        ] },
                        React.createElement(List.Item.Meta, { title: React.createElement(Space, { wrap: true },
                                React.createElement("span", { style: { fontWeight: 600 } }, job.name),
                                React.createElement(Tag, { icon: React.createElement(ClockCircleOutlined, null), color: "default" }, type)), description: React.createElement("div", null,
                                React.createElement("div", { className: styles.jobMeta },
                                    React.createElement(ScheduleOutlined, { className: styles.jobMetaIcon }),
                                    React.createElement("span", null,
                                        "Pipeline: ",
                                        job.pipeline_path)),
                                job.next_run_time && (React.createElement("div", { className: styles.jobMeta },
                                    React.createElement(CalendarOutlined, { className: styles.jobMetaIcon }),
                                    React.createElement("span", null,
                                        "Next: ",
                                        dayjs(job.next_run_time).format('YYYY-MM-DD HH:mm:ss'))))) })));
                } }))),
            React.createElement(Modal, { title: currentJob ? 'Edit Task' : 'New Task', open: jobModalVisible, onCancel: () => setJobModalVisible(false), footer: null, destroyOnClose: true, width: 500 },
                React.createElement(JobForm, { docManager: docManager, onSubmit: handleFormSubmit, onCancel: () => setJobModalVisible(false), initialValues: currentJob || undefined })))));
};
/* ---------- plugin ---------- */
var CommandIDs;
(function (CommandIDs) {
    CommandIDs.open = 'pipeline-scheduler:open';
})(CommandIDs || (CommandIDs = {}));
const plugin = {
    id: '@amphi/pipeline-scheduler:plugin',
    autoStart: true,
    requires: [ICommandPalette, IDocumentManager],
    activate: (app, palette, docManager) => {
        const { commands, shell } = app;
        commands.addCommand(CommandIDs.open, {
            label: 'Pipeline Scheduler',
            caption: 'Schedule Amphi pipelines',
            execute: () => {
                class SchedulerWidget extends ReactWidget {
                    constructor() {
                        super();
                        this.id = 'amphi-pipeline-scheduler';
                        this.title.caption = 'Pipeline Scheduler';
                        this.title.icon = schedulerIcon;
                        this.title.closable = true;
                    }
                    render() {
                        return React.createElement(SchedulerPanel, { commands: commands, docManager: docManager });
                    }
                }
                const widget = new SchedulerWidget();
                if (!widget.isAttached)
                    shell.add(widget, 'left');
                shell.activateById(widget.id);
            }
        });
        palette.addItem({ command: CommandIDs.open, category: 'Amphi' });
        commands.execute(CommandIDs.open);
    }
};
export default plugin;
