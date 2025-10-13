/**
* @license
* SPDX-FileCopyrightText: © 2021 Josef Hahn
* SPDX-License-Identifier: AGPL-3.0-only
*/

import { backend, sanitizePath } from "../backend/common.js";
import { baseStylesRef } from "../piweb/styling.js";

const panelTemplate = document.createElement("template");
panelTemplate.innerHTML = `
    ${baseStylesRef()}
    <style>
        :host {
            display: block;
            overflow: hidden;
            margin: 0.3em;
        }
        #lblfilename {
            text-overflow: ellipsis;
            overflow: hidden;
        }
        .panelpiece {
            display: grid;
            grid-template-columns: auto 1fr;
            grid-template-rows: auto auto;
            border-left: 0.25em solid #ffffff22;
            margin: 0.5em;
            float: left;
        }
        .panelpiece .panelpieceactionpanel {
            grid-column: 2;
        }
        .panelpiece .panelpieceactionpanel sl-button {
            margin: 0.25rem;
        }
        .panelpiece .panelpiecewidget {
            grid-row: 2;
            grid-column: 1 / 3;
        }
        .panelpiece .panelpiecelbl {
            opacity: 0.5;
        }
    </style>
    <div id="main">
        <div id="lblfilename"></div>
        <div id="pnlpieces"></div>
    </div>
`;

/**
* A bunch of file information.
*/
export class DetailsPanel extends HTMLElement {

    constructor() {
        super();
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(panelTemplate.content.cloneNode(true));
        this._main = this._shadow.getElementById("main");
        this._lblfilename = this._shadow.getElementById("lblfilename");
        this._pnlpieces = this._shadow.getElementById("pnlpieces");
        this._paths = [];
        this._entry = undefined;
        this._populate();
    }

    static get observedAttributes() {
        return ["access-mode"];
    }

    /**
    * The access mode (controls visibility of some actions).
    */
    get accessMode() {
        return this.getAttribute("access-mode");
    }

    set accessMode(v) {
        this.setAttribute("access-mode", v);
    }

    get accessModeIsReadWrite() {
        return this.accessMode === "readwrite";
    }

    attributeChangedCallback(name, oldVal, newVal) {
        if (name === "access-mode")
            this._populate();
    }

    _createPiece(label, widget, actionpanel) {
        const piece = document.createElement("div");
        piece.className = "panelpiece";
        const piecelbl = document.createElement("div");
        piecelbl.className = "panelpiecelbl";
        piecelbl.textContent = label;
        piece.appendChild(piecelbl);
        widget.classList.add("panelpiecewidget");
        piece.appendChild(widget);
        if (actionpanel) {
            actionpanel.classList.add("panelpieceactionpanel");
            piece.appendChild(actionpanel);
        }
        return piece;
    }

    /**
    * The paths to show.
    */
    get paths() {
        return this._paths;
    }

    set paths(v) {
        this._paths = v;
        this._entry = (v.length === 1) ? backend.entryDetails(v[0]) : undefined;
        this._populate();
    }

    _pathBasename(p) {
        const ilastslash = p.lastIndexOf("/");
        if (ilastslash > -1)
            p = p.substring(ilastslash + 1);
        return p;
    }

    async _populate() {
        if (this._paths.length > 0) {
            this._lblfilename.textContent = (this._paths.length === 1)
                ? this._pathBasename(this._paths[0])
                : `${this._paths.length} items`;
            this._pnlpieces.innerHTML = "";
            const reqhandle = this._entrydetails_reqhandle = new Object();
            const entry = await this._entry;
            if (reqhandle !== this._entrydetails_reqhandle)
                return;
            for (const [piecedomtype, piecelabel] of [
                ["openactions", ""],
                ["modifyactions", ""],
                ["comment", "Comment"],
                ["tags", "Tags"],
                ["rating", "Rating"],
                ["geo", "Geo"],
                ["filesize", "Size"],
                ["mtime", "Last modified"],
                ["preview", "Preview"]
            ]) {
                const piecepanel = document.createElement(`lawwenda-detailspanel-${piecedomtype}`);
                if (piecepanel.isVisible && !piecepanel.isVisible(this, this._paths, entry))
                    continue;
                const pieceactionspanel = piecepanel.createActionPanel
                    ? piecepanel.createActionPanel(this, this._paths, entry)
                    : undefined;
                this._pnlpieces.appendChild(this._createPiece(piecelabel, piecepanel, pieceactionspanel));
                piecepanel.populate(this, this._paths, entry);
            }
        }
        else {
            this._lblfilename.textContent = "";
            this._pnlpieces.textContent = "Select an item for more details.";
        }
    }

}

customElements.define("lawwenda-detailspanel", DetailsPanel);

function createButton(text, iconname) {
    const btn = document.createElement("sl-button");
    btn.size = "small";
    if (iconname) {
        const btnico = document.createElement("sl-icon");
        btnico.name = iconname;
        btn.appendChild(btnico);
        btn.append(" ");
    }
    btn.append(text);
    return btn;
}

const detailsstyle = `
    <style>
        sl-button {
            margin: 0.25em;
        }
    </style>
`;

const openactionsPanelTemplate = document.createElement("template");
openactionsPanelTemplate.innerHTML = `
    ${baseStylesRef()}
    ${detailsstyle}
    <div id="main">
    </div>
`;

/**
* Open action details.
*/
export class DetailsPanelOpenActions extends HTMLElement {

    constructor() {
        super();
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(openactionsPanelTemplate.content.cloneNode(true));
        this._main = this._shadow.getElementById("main");
    }

    populate(detailsPanel, paths, entry) {
        const self = this;
        this._main.innerHTML = "";
        for (const [actionlabel, actionicon, eventname] of [
            ["Open", "box-arrow-up-right", "pathSelected"],
            ["Download as Zip", "file-zip", "downloadzip"]
        ]) {
            if (eventname === "downloadzip" && !(entry?.is_dir || paths.length > 1))
                continue;
            if (eventname === "pathSelected" && paths.length > 1)
                continue;
            const btn = createButton(actionlabel, actionicon);
            if (eventname === "pathSelected" && !entry?.is_dir) {
                const tgturl = new URL(document.location.href);
                tgturl.pathname = "/" + sanitizePath(`${tgturl.path}/${entry?.name}`);
                btn.type = "primary";
                btn.href = tgturl.href;
                btn.target = "_blank";
            }
            else
                btn.addEventListener("click", () => {
                    self.dispatchEvent(new CustomEvent(eventname, {
                        detail: { paths: paths }, bubbles: true, composed: true
                    }));
                });
            this._main.appendChild(btn);
        }
    }

}

customElements.define("lawwenda-detailspanel-openactions", DetailsPanelOpenActions);

const modifyactionsPanelTemplate = document.createElement("template");
modifyactionsPanelTemplate.innerHTML = `
    ${baseStylesRef()}
    ${detailsstyle}
    <div id="main">
    </div>
`;

/**
* Modify actions details.
*/
export class DetailsPanelModifyActions extends HTMLElement {

    constructor() {
        super();
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(modifyactionsPanelTemplate.content.cloneNode(true));
        this._main = this._shadow.getElementById("main");
    }

    isVisible(detailsPanel, paths, entry) {
        return detailsPanel.accessModeIsReadWrite;
    }

    populate(detailsPanel, paths, entry) {
        const self = this;
        this._main.innerHTML = "";
        for (const [actionlabel, actionicon, eventname] of [
            ["Copy", "arrow-up-right-circle-fill", "copy"],
            ["Move", "arrow-up-right-circle", "move"],
            ["Rename", "pencil", "rename"],
            ["Delete", "trash", "delete"]
        ]) {
            if (eventname === "rename" && paths.length > 1)
                continue;
            const btn = createButton(actionlabel, actionicon);
            btn.addEventListener("click", () => {
                self.dispatchEvent(new CustomEvent(eventname, {
                    detail: { paths: paths }, bubbles: true, composed: true
                }));
            });
            this._main.appendChild(btn);
        }
    }

}

customElements.define("lawwenda-detailspanel-modifyactions", DetailsPanelModifyActions);

const commentPanelTemplate = document.createElement("template");
commentPanelTemplate.innerHTML = `
    ${baseStylesRef()}
    ${detailsstyle}
    <div id="main">
    </div>
`;

/**
* Comment details.
*/
export class DetailsPanelComment extends HTMLElement {

    constructor() {
        super();
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(commentPanelTemplate.content.cloneNode(true));
        this._main = this._shadow.getElementById("main");
    }

    createActionPanel(detailsPanel, paths, entry) {
        const self = this;
        const result = document.createElement("div");
        if (detailsPanel.accessModeIsReadWrite) {
            const btnchange = createButton("", "pencil-square");
            btnchange.addEventListener("click", () => {
                self.dispatchEvent(new CustomEvent("changecomment", {
                    detail: { paths: paths }, bubbles: true, composed: true
                }));
            });
            btnchange.circle = true;
            result.appendChild(btnchange);
        }
        return result;
    }

    populate(detailsPanel, paths, entry) {
        this._main.textContent = entry ? entry.comment : "...";
    }

}

customElements.define("lawwenda-detailspanel-comment", DetailsPanelComment);

const tagsPanelTemplate = document.createElement("template");
tagsPanelTemplate.innerHTML = `
    ${baseStylesRef()}
    ${detailsstyle}
    <div id="main">
    </div>
`;

/**
* Tags details.
*/
export class DetailsPanelTags extends HTMLElement {

    constructor() {
        super();
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(tagsPanelTemplate.content.cloneNode(true));
        this._main = this._shadow.getElementById("main");
    }

    createActionPanel(detailsPanel, paths, entry) {
        const self = this;
        const result = document.createElement("div");
        if (detailsPanel.accessModeIsReadWrite) {
            for (const [actionicon, eventname] of [["plus", "addtag"], ["dash", "removetag"]]) {
                const btn = createButton("", actionicon);
                btn.circle = true;
                btn.addEventListener("click", () => {
                    self.dispatchEvent(new CustomEvent(eventname, {
                        detail: { paths: paths }, bubbles: true, composed: true
                    }));
                });
                result.appendChild(btn);
            }
        }
        return result;
    }

    populate(detailsPanel, paths, entry) {
        const self = this;
        if (entry) {
            for (const tag of entry.tags) {
                const tagbtn = createButton(tag);
                tagbtn.classList.add("tag");
                tagbtn.pill = true;
                tagbtn.addEventListener("click", () => {
                    self.dispatchEvent(new CustomEvent("browsetag", {
                        detail: { tag: tag }, bubbles: true, composed: true
                    }));
                });
                this._main.appendChild(tagbtn);
            }
        }
    }

}

customElements.define("lawwenda-detailspanel-tags", DetailsPanelTags);

const ratingPanelTemplate = document.createElement("template");
ratingPanelTemplate.innerHTML = `
    ${baseStylesRef()}
    ${detailsstyle}
    <sl-rating precision="0.5" max="5" id="rating">
    </sl-rating>
`;

/**
* Rating details.
*/
export class DetailsPanelRating extends HTMLElement {

    constructor() {
        super();
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(ratingPanelTemplate.content.cloneNode(true));
        this._rating = this._shadow.getElementById("rating");
    }

    populate(detailsPanel, paths, entry) {
        const self = this;
        if (entry)
            this._rating.value = entry.rating / 2;
        if (!detailsPanel.accessModeIsReadWrite)
            this._rating.readonly = true;
        this._rating.addEventListener("sl-change", (event) => {
            self.dispatchEvent(new CustomEvent("changerating", {
                detail: { paths: paths, rating: event.originalTarget.value * 2 }, bubbles: true, composed: true
            }));
        });
    }

}

customElements.define("lawwenda-detailspanel-rating", DetailsPanelRating);

const geoPanelTemplate = document.createElement("template");
geoPanelTemplate.innerHTML = `
    ${baseStylesRef()}
    ${detailsstyle}
    <style>
        #main {
            height: 6rem;
            width: 9rem;
            overflow: hidden;
            border-radius: 0.5rem;
        }
        #main.geolarge {
            height: 15rem;
            width: 20rem;
        }
    </style>
    <piweb-map id="main" user-may-move="no" zoom-control-visible="no">
    </piweb-map>
`;

/**
* Geo details.
*/
export class DetailsPanelGeo extends HTMLElement {

    constructor() {
        super();
        const self = this;
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(geoPanelTemplate.content.cloneNode(true));
        this._main = this._shadow.getElementById("main");
        this.large = false;
        this._main.addEventListener("click", () => {
            self.large = !self.large;
        });
    }

    get large() {
        return this._large;
    }

    set large(v) {
        this._large = v;
        if (v)
            this._main.classList.add("geolarge");
        else
            this._main.classList.remove("geolarge");
        window.dispatchEvent(new Event("resize"));
    }

    createActionPanel(detailsPanel, paths, entry) {
        const self = this;
        const result = document.createElement("div");
        if (detailsPanel.accessModeIsReadWrite) {
            const btnchange = createButton("", "geo");
            btnchange.addEventListener("click", () => {
                self.dispatchEvent(new CustomEvent("changegeo", {
                    detail: { paths: paths }, bubbles: true, composed: true
                }));
            });
            btnchange.circle = true;
            result.appendChild(btnchange);
        }
        return result;
    }

    populate(detailsPanel, paths, entry) {
        if (entry?.geo) {
            this._main.position = entry.geo;
            this._main.zoomLevel = 9;
            this._main.addCircle(this._main.position, { radius: parseFloat(this._main.position?.auxargs?.acc || 0.1) });
        }
        else
            this._main.style.display = "none";
    }

}

customElements.define("lawwenda-detailspanel-geo", DetailsPanelGeo);

const filesizePanelTemplate = document.createElement("template");
filesizePanelTemplate.innerHTML = `
    ${baseStylesRef()}
    ${detailsstyle}
    <div id="main">
    </div>
`;

/**
* File size details.
*/
export class DetailsPanelFilesize extends HTMLElement {

    constructor() {
        super();
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(filesizePanelTemplate.content.cloneNode(true));
        this._main = this._shadow.getElementById("main");
    }

    isVisible(detailsPanel, paths, entry) {
        return Boolean(entry) && entry.is_file;
    }

    populate(detailsPanel, paths, entry) {
        if (entry)
            this._main.textContent = `${entry.size.toLocaleString()} byte`;
    }

}

customElements.define("lawwenda-detailspanel-filesize", DetailsPanelFilesize);

const mtimePanelTemplate = document.createElement("template");
mtimePanelTemplate.innerHTML = `
    ${baseStylesRef()}
    ${detailsstyle}
    <div id="main">
    </div>
`;

/**
* Modification time details.
*/
export class DetailsPanelMtime extends HTMLElement {

    constructor() {
        super();
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(mtimePanelTemplate.content.cloneNode(true));
        this._main = this._shadow.getElementById("main");
    }

    isVisible(detailsPanel, paths, entry) {
        return Boolean(entry);
    }

    populate(detailsPanel, paths, entry) {
        if (entry)
            this._main.textContent = new Date(entry.mtime_ts * 1000).toLocaleString();
    }

}

customElements.define("lawwenda-detailspanel-mtime", DetailsPanelMtime);

const previewPanelTemplate = document.createElement("template");
previewPanelTemplate.innerHTML = `
    ${baseStylesRef()}
    ${detailsstyle}
    <style>
        .previewerpiece {
            max-width: var(--previewerpiece-width, 1em);
            max-height: var(--previewerpiece-height, 1em);
        }
    </style>
    <div id="main">
    </div>
`;

/**
* Modification time details.
*/
export class DetailsPanelPreview extends HTMLElement {

    constructor() {
        super();
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(previewPanelTemplate.content.cloneNode(true));
        this._main = this._shadow.getElementById("main");
    }

    isVisible(detailsPanel, paths, entry) {
        return Boolean(entry?.preview_html);
    }

    createActionPanel(detailsPanel, paths, entry) {
        const self = this;
        const result = document.createElement("div");
        for (const [actionicon, eventname] of [
            ["fullscreen", "resizepanel"],
            ["chevron-left", "selectpreviousentry"],
            ["chevron-right", "selectnextentry"]
        ]) {
            const btn = createButton("", actionicon);
            if (eventname === "selectpreviousentry" || eventname === "selectnextentry")
                btn.classList.add("only-visible-in-fullsizedetails-mode");
            btn.addEventListener("click", () => {
                self.dispatchEvent(new CustomEvent(eventname, { detail: {}, bubbles: true, composed: true }));
            });
            btn.circle = true;
            result.appendChild(btn);
        }
        return result;
    }

    populate(detailsPanel, paths, entry) {
        if (entry)
            this._main.innerHTML = entry?.preview_html;
    }

}

customElements.define("lawwenda-detailspanel-preview", DetailsPanelPreview);
