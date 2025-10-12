import React from 'react';
import ReactDOM from 'react-dom';
import { Switch, ConfigProvider, Typography } from 'antd';
import { Dialog } from '@jupyterlab/apputils';
import { BreadCrumbs, DirListing, FilterFileBrowserModel } from '@jupyterlab/filebrowser';
import { Widget, PanelLayout } from '@lumino/widgets';
const BROWSE_FILE_CLASS = 'amphi-browseFileDialog';
const BROWSE_FILE_OPEN_CLASS = 'amphi-browseFileDialog-open';
const { Text } = Typography;
/* ───────────────────────── breadcrumbs ───────────────────────── */
class BrowseFileDialogBreadcrumbs extends BreadCrumbs {
    constructor(options) {
        super(options);
        this.model = options.model;
        this.rootPath = options.rootPath;
    }
    onUpdateRequest(msg) {
        super.onUpdateRequest(msg);
        const contents = this.model.manager.services.contents;
        const localPath = contents.localPath(this.model.path);
        if (localPath && this.rootPath && localPath.indexOf(this.rootPath) === 0) {
            const crumbs = document.querySelectorAll(`.${BROWSE_FILE_CLASS} .jp-BreadCrumbs > span[title]`);
            crumbs.forEach(c => {
                var _a;
                const s = c;
                if (s.title.indexOf((_a = this.rootPath) !== null && _a !== void 0 ? _a : '') === 0) {
                    s.className = s.className.replace('amphi-BreadCrumbs-disabled', '').trim();
                }
                else if (s.className.indexOf('amphi-BreadCrumbs-disabled') === -1) {
                    s.className += ' amphi-BreadCrumbs-disabled';
                }
            });
        }
    }
}
/* ─────────────────────── main widget ─────────────────────────── */
class BrowseFileDialog extends Widget {
    constructor(props) {
        var _a;
        super(props);
        this.switchWidget = null;
        this.showAll = false;
        /* filter definitions */
        this.baseFilter = props.filter || (() => true);
        // The extFilter checks file extensions
        this.extFilter =
            props.extensions && props.extensions.length
                ? (m) => {
                    if (m.type === 'directory')
                        return true; // Always show directories
                    const ext = `.${m.name.split('.').pop().toLowerCase()}`;
                    return props.extensions.includes(ext);
                }
                : (() => true); // If no extensions are provided, show everything
        // Initialize the model with the extension filter
        this.model = new FilterFileBrowserModel({
            manager: props.manager,
            filter: BrowseFileDialog.boolToScore((m) => {
                // Apply base filter first (user-provided filter)
                if (!this.baseFilter(m))
                    return false;
                // Then apply extension filter if not showing all
                if (!this.showAll && m.type !== 'directory') {
                    const ext = `.${m.name.split('.').pop().toLowerCase()}`;
                    return props.extensions && props.extensions.length ?
                        props.extensions.includes(ext) : true;
                }
                return true;
            })
        });
        const layout = (this.layout = new PanelLayout());
        /* breadcrumbs */
        this.breadCrumbs = new BrowseFileDialogBreadcrumbs({
            model: this.model,
            rootPath: props.rootPath
        });
        layout.addWidget(this.breadCrumbs);
        /* toggle switch + label */
        if (props.extensions && props.extensions.length) {
            const container = document.createElement('div');
            // Create a render function that can be called to update the UI
            const renderSwitchUI = (showAllFiles) => {
                ReactDOM.render(React.createElement("div", { style: { marginBottom: '10px' } },
                    React.createElement(ConfigProvider, { theme: {
                            token: {
                                // Seed Token
                                colorPrimary: '#5F9B97',
                            },
                        } },
                        React.createElement("div", { style: { display: 'flex', alignItems: 'center', gap: '8px' } },
                            React.createElement("span", { style: { flexShrink: 0 } },
                                React.createElement(Switch, { checked: showAllFiles, size: "small", style: {
                                        width: '28px',
                                        minWidth: '28px',
                                        height: '16px',
                                        lineHeight: '16px'
                                    }, onChange: (checked) => {
                                        this.showAll = checked;
                                        // Update the filter based on the switch state
                                        this.model.setFilter(BrowseFileDialog.boolToScore((m) => {
                                            // Always apply base filter
                                            if (!this.baseFilter(m))
                                                return false;
                                            // Apply extension filter only when showAll is false and it's a file
                                            if (!checked && m.type !== 'directory') {
                                                const ext = `.${m.name.split('.').pop().toLowerCase()}`;
                                                return props.extensions && props.extensions.length ?
                                                    props.extensions.includes(ext) : true;
                                            }
                                            return true;
                                        }));
                                        // Re-render with the new state
                                        renderSwitchUI(checked);
                                        void this.model.refresh();
                                    } })),
                            React.createElement("span", { style: { fontSize: '14px' } }, showAllFiles ? "Show all files" : "Only show relevant files")))), container);
            };
            // Initial render
            renderSwitchUI(this.showAll);
            this.switchWidget = new Widget({ node: container });
            layout.insertWidget(1, this.switchWidget); // directly under breadcrumbs
        }
        /* directory listing */
        this.directoryListing = new DirListing({ model: this.model });
        this.acceptFileOnDblClick = (_a = props.acceptFileOnDblClick) !== null && _a !== void 0 ? _a : true;
        this.multiselect = !!props.multiselect;
        this.includeDir = !!props.includeDir;
        this.dirListingHandleEvent = this.directoryListing.handleEvent;
        this.directoryListing.handleEvent = (e) => { this.handleEvent(e); };
        layout.addWidget(this.directoryListing);
    }
    /* factory */
    static async init(options) {
        const dlg = new BrowseFileDialog({
            manager: options.manager,
            extensions: options.extensions,
            filter: options.filter || (() => true),
            multiselect: options.multiselect,
            includeDir: options.includeDir,
            rootPath: options.rootPath,
            startPath: options.startPath,
            acceptFileOnDblClick: options.acceptFileOnDblClick
        });
        if (options.startPath) {
            if (!options.rootPath || options.startPath.indexOf(options.rootPath) === 0) {
                await dlg.model.cd(options.startPath);
            }
        }
        else if (options.rootPath) {
            await dlg.model.cd(options.rootPath);
        }
        return dlg;
    }
    /* result */
    getValue() {
        const selected = [];
        for (const item of this.directoryListing.selectedItems()) {
            if (this.includeDir || item.type !== 'directory')
                selected.push(item);
        }
        return selected;
    }
    /* event proxy */
    handleEvent(event) {
        var _a;
        let modifierKey = false;
        if (event instanceof MouseEvent || event instanceof KeyboardEvent) {
            modifierKey = event.shiftKey || event.metaKey;
        }
        switch (event.type) {
            case 'keydown':
            case 'keyup':
            case 'mousedown':
            case 'mouseup':
            case 'click':
                if (this.multiselect || !modifierKey) {
                    this.dirListingHandleEvent.call(this.directoryListing, event);
                }
                break;
            case 'dblclick': {
                const clicked = this.directoryListing.modelForClick(event);
                if ((clicked === null || clicked === void 0 ? void 0 : clicked.type) === 'directory') {
                    this.dirListingHandleEvent.call(this.directoryListing, event);
                }
                else {
                    event.preventDefault();
                    event.stopPropagation();
                    if (this.acceptFileOnDblClick) {
                        (_a = document.querySelector(`.${BROWSE_FILE_OPEN_CLASS} .jp-mod-accept`)) === null || _a === void 0 ? void 0 : _a.click();
                    }
                }
                break;
            }
            default:
                this.dirListingHandleEvent.call(this.directoryListing, event);
                break;
        }
    }
}
/**
 * Helper function to convert a boolean predicate to a score function that the FileBrowserModel accepts
 */
BrowseFileDialog.boolToScore = (pred) => (m) => (pred(m) ? {} : null);
/* ───────────────────────── helper ───────────────────────────── */
export const showBrowseFileDialog = async (manager, options) => {
    const body = await BrowseFileDialog.init({
        manager,
        extensions: options.extensions,
        filter: options.filter,
        multiselect: options.multiselect,
        includeDir: options.includeDir,
        rootPath: options.rootPath,
        startPath: options.startPath,
        acceptFileOnDblClick: Object.prototype.hasOwnProperty.call(options, 'acceptFileOnDblClick')
            ? options.acceptFileOnDblClick
            : true
    });
    const dialog = new Dialog({
        title: 'Select a file',
        body,
        buttons: [Dialog.cancelButton(), Dialog.okButton({ label: 'Select' })]
    });
    dialog.addClass(BROWSE_FILE_CLASS);
    document.body.className += ` ${BROWSE_FILE_OPEN_CLASS}`;
    return dialog.launch().then(result => {
        document.body.className = document.body.className
            .replace(BROWSE_FILE_OPEN_CLASS, '')
            .trim();
        if (options.rootPath && result.button.accept && result.value.length) {
            const root = options.rootPath.endsWith('/') ? options.rootPath : `${options.rootPath}/`;
            result.value.forEach((v) => { v.path = v.path.replace(root, ''); });
        }
        return result;
    });
};
