/**
* @license
* SPDX-FileCopyrightText: © 2021 Josef Hahn
* SPDX-License-Identifier: AGPL-3.0-only
*/

import { backend, getThumbnailUrl, relativePathByRefPath, urlInternalsName } from "../backend/common.js";
import { BusyElementController } from "../piweb/busy.js";
import { baseStylesRef } from "../piweb/styling.js";

const dirviewTemplate = document.createElement("template");
dirviewTemplate.innerHTML = `
    ${baseStylesRef()}
    <style>
        .fsentry {
            border-bottom: 0.125em solid gray;
            display: grid;
            grid-template-rows: auto auto;
            column-gap: 0.35em;
            grid-template-columns: auto 1fr auto auto 0;
            transition: background 0.4s;
            cursor: default;
            font-size: 0.9rem;
        }
        #list.dragging .fsentry:not(.selected) {
            opacity: 0;
        }
        .fsentry.selected {
            background: #3355ff22;
        }
        .fsentry:hover {
            background: #3355ff44;
        }
        .fsentry.selected:hover {
            background: #3355ff66;
        }
        .fsentry .thumb {
            grid-row: 1 / 3;
            grid-column: 1;
            height: var(--icon-size, 1rem);
            width: var(--icon-size, 1rem);
        }
        .fsentry .name {
            grid-row: 1 / 3;
            grid-column: 2;
            font-size: 1.2rem;
            word-wrap: anywhere;
        }
        .fsentry .size {
            grid-row: 1;
            grid-column: 4;
            text-align: right;
        }
        .fsentry .mtimelbl {
            grid-row: 2;
            grid-column: 3;
            opacity: 0.5;
        }
        .fsentry .mtime {
            grid-row: 2;
            grid-column: 4;
            text-align: right;
        }
    </style>
    <div id="list">
    </div>
`;

/**
* A directory content view, i.e. a list of all files and subdirectories.
*/
export class DirectoryView extends HTMLElement {

    constructor() {
        super();
        const self = this;
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(dirviewTemplate.content.cloneNode(true));
        this._busyctrl = new BusyElementController(this._shadow, "busy_fadein", "busy_fadeout");
        this._list = this._shadow.getElementById("list");
        this._selectedEntries = [];
        this._entries = [];
        this._list.tabIndex = 0;
        this._srcdir = undefined;
        this._list.addEventListener("keydown", (event) => {
            const navby = {
                "ArrowUp": -1,
                "ArrowDown": +1,
                "PageUp": -5,
                "PageDown": +5,
                "Home": -this._entries.length,
                "End": +this._entries.length
            }[event.key];
            if (navby) {
                event.stopPropagation();
                event.preventDefault();
                self.selectEntryByOffset(navby);
                self.scrollToSelection();
            }
        });
        this._list.draggable = true;
        this._list.addEventListener("dragstart", (event) => {
            this._list.classList.add("dragging");
            let surls = "";
            for (const entry of self._selectedEntries) {
                const rurl = new URL(document.location.href);
                // we assume that entry.path starts with self.path (is not outside of the current dir)
                rurl.pathname += "/" + relativePathByRefPath(entry.path, self.path);
                rurl.search = "";
                surls += rurl.href + "\r\n";
            }
            event.dataTransfer.setData("text/uri-list", surls);
            event.dataTransfer.setData("text/plain", surls);
        });
        this._list.addEventListener("dragend", (event) => {
            this._list.classList.remove("dragging");
        });
        this._list.addEventListener("dragenter", (event) => {
            event.preventDefault();
            event.dataTransfer.effectAllowed = "all";
            event.dataTransfer.dropEffect = "copy";
        });
        this._list.addEventListener("dragover", (event) => {
            event.preventDefault();
        });
        this._list.addEventListener("drop", (event) => {
            event.preventDefault();
            self.dispatchEvent(new CustomEvent("uploadEntries", {
                detail: { destpath: self.path, files: event.dataTransfer.files }, bubbles: true
            }));
        });
    }

    static get observedAttributes() {
        return ["is-hidden-files-visible", "path", "search-config", "sort-column", "sort-descending"];
    }

    /**
    * The search configuration dict.
    */
    get searchConfig() {
        return this.getAttribute("search-config");
    }

    set searchConfig(v) {
        this.setAttribute("search-config", v);
    }

    /**
    * The sort column name.
    */
    get sortColumn() {
        return this.getAttribute("sort-column");
    }

    set sortColumn(v) {
        this.setAttribute("sort-column", v);
    }

    /**
    * If to descend the sorting of elements.
    */
    get sortDescending() {
        return this.hasAttribute("sort-descending");
    }

    set sortDescending(v) {
        if (v)
            this.setAttribute("sort-descending", v);
        else
            this.removeAttribute("sort-descending");
    }

    /**
    * If to show hidden files as well.
    */
    get isHiddenFilesVisible() {
        return this.hasAttribute("is-hidden-files-visible");
    }

    set isHiddenFilesVisible(v) {
        if (v)
            this.setAttribute("is-hidden-files-visible", v);
        else
            this.removeAttribute("is-hidden-files-visible");
    }

    /**
    * The directory to show.
    */
    get path() {
        return this.getAttribute("path");
    }

    set path(v) {
        this.setAttribute("path", v);
    }

    attributeChangedCallback(name, oldVal, newVal) {
        if (name === "path")
            this._srcdir = newVal;
        if (DirectoryView.observedAttributes.includes(name))
            this._populate();
    }

    _populate() {
        this._list.innerHTML = "";
        this._update();
    }

    _toFriendlyByteSize(value) {
        let prefix = "";
        for (const p of ["k", "M", "G", "T", "P", "E", "Z", "Y"]) {
            if (value >= 1024) {
                value = value / 1024;
                prefix = p;
            }
        }
        return `${value.toFixed(1)} ${prefix}byte`;
    }

    selectEntry(entry) {
        this._selectedEntries = [entry];
        for (const childnode of this._list.childNodes) {
            if (childnode._name === entry.name)
                childnode.classList.add("selected");
            else
                childnode.classList.remove("selected");
        }
        this.dispatchEvent(new CustomEvent("entriesSelected", {
            detail: { paths: this.selectedPaths }, bubbles: true
        }));
    }

    resetSelection() {
        for (const entry of this.selectedEntries)
            this.removeEntryFromSelection(entry);
    }

    indexForEntry(entry) {
        for (let ientry = 0; ientry < this._entries.length; ientry++) {
            if (this._entries[ientry].name === entry.name)
                return ientry;
        }
        return -1;
    }

    scrollToSelection() {
        const sel = this._selectedEntries;
        if (sel.length > 0) {
            for (const childnode of this._list.childNodes) {
                if (childnode._name === sel[0].name) {
                    childnode.scrollIntoView({ block: "center", behavior: "smooth" });
                    break;
                }
            }
        }
    }

    selectEntryByOffset(offset) {
        let sel = this._selectedEntries;
        if (sel.length === 0)
            sel = this._entries;
        if (sel.length > 0) {
            let isele = this.indexForEntry(sel[0]);
            isele = Math.min(Math.max(0, isele + offset), this._entries.length - 1);
            this.selectEntry(this._entries[isele]);
        }
    }

    get allEntries() {
        return this._entries;
    }

    addEntryToSelection(entry) {
        this._selectedEntries.push(entry);
        for (const childnode of this._list.childNodes) {
            if (childnode._name === entry.name)
                childnode.classList.add("selected");
        }
    }

    removeEntryFromSelection(entry) {
        this._selectedEntries = this._selectedEntries.filter(e => e.name !== entry.name);
        for (const childnode of this._list.childNodes) {
            if (childnode._name === entry.name)
                childnode.classList.remove("selected");
        }
    }

    get selectedEntries() {
        return this._selectedEntries;
    }

    get selectedPaths() {
        return this.selectedEntries.map(e => e.path);
    }

    async _update() {
        const self = this;
        if (this._srcdir === undefined)
            return;
        const reqhandle = this._listdir_reqhandle = new Object();
        this._busyctrl.setBusy();
        const entries = await backend.listDirectoryEntries(this._srcdir, {
            hiddenFilesVisible: this.isHiddenFilesVisible,
            searchConfig: this.searchConfig,
            sortColumn: this.sortColumn,
            sortDescending: this.sortDescending
        });
        if (reqhandle !== this._listdir_reqhandle)
            return;
        this._busyctrl.unsetBusy();
        this._entries = entries;
        for (const entry of entries) {
            const entrydiv = document.createElement("div");
            entrydiv._name = entry.name;
            entrydiv.className = "fsentry";
            const entrythumbdiv = document.createElement("img");
            entrythumbdiv.className = "thumb";
            entrythumbdiv.src = entry.icon_name
                ? `${urlInternalsName}/static/img/${entry.icon_name}.svg`
                : getThumbnailUrl(entry.path);
            entrydiv.appendChild(entrythumbdiv);
            const entrynamediv = document.createElement("div");
            entrynamediv.className = "name";
            entrynamediv.textContent = entry.name;
            entrydiv.appendChild(entrynamediv);
            const entrymtimelbldiv = document.createElement("div");
            entrymtimelbldiv.className = "mtimelbl";
            entrymtimelbldiv.textContent = "modified:";
            entrydiv.appendChild(entrymtimelbldiv);
            if (!entry.is_dir) {
                const entrysizediv = document.createElement("div");
                entrysizediv.className = "size";
                entrysizediv.textContent = this._toFriendlyByteSize(entry.size);
                entrydiv.appendChild(entrysizediv);
            }
            const entrymtimediv = document.createElement("div");
            entrymtimediv.className = "mtime";
            entrymtimediv.textContent = new Date(entry.mtime_ts * 1000).toLocaleString();
            entrydiv.appendChild(entrymtimediv);
            this._list.appendChild(entrydiv);
            entrythumbdiv.addEventListener("click", (event) => {
                event.stopPropagation();
                if (self.selectedEntries.some(e => e.name === entry.name))
                    self.removeEntryFromSelection(entry);
                else
                    self.addEntryToSelection(entry);
                self.dispatchEvent(new CustomEvent("entriesSelected", {
                    detail: { paths: self.selectedPaths }, bubbles: true
                }));
            });
            entrydiv.addEventListener("click", () => {
                self.selectEntry(entry);
            });
            entrydiv.addEventListener("dblclick", () => {
                if (entry.is_dir)
                    self.dispatchEvent(new CustomEvent("pathSelected", {
                        detail: { path: entry.path }, bubbles: true
                    }));
                else
                    self.dispatchEvent(new CustomEvent("openFile", {
                        detail: { path: entry.path }, bubbles: true
                    }));
            });
        }
    }

}

customElements.define("lawwenda-directoryview", DirectoryView);
