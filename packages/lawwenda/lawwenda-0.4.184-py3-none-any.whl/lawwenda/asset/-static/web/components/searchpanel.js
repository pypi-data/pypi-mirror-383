/**
* @license
* SPDX-FileCopyrightText: © 2021 Josef Hahn
* SPDX-License-Identifier: AGPL-3.0-only
*/

import { baseStylesRef } from "../piweb/styling.js";

const panelTemplate = document.createElement("template");
panelTemplate.innerHTML = `
    ${baseStylesRef()}
    <style>
        :host {
            display: block;
            position: relative;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--panel-bgcolor);
            border-radius: 0.5rem;
            box-sizing: border-box;
            box-shadow: 0 0 8pt black;
        }
        #main {
            width: 100%;
            display: grid;
            color: var(--panel-fgcolor);
            grid-template-rows: auto auto;
            grid-template-columns: 1fr auto;
        }
        #configpanel {
            display: none;
            grid-row: 2;
            grid-column: 1 / 3;
            margin: 1rem;
            overflow: auto;
        }
        .expanded #configpanel {
            display: revert;
        }
        #main.expanded {
            height: var(--expanded-height);
        }
        #head {
            grid-row: 1;
            grid-column: 1;
            margin: 0 1rem;
            font-size: 1.1rem;
            text-overflow: ellipsis;
            overflow: hidden;
            white-space: nowrap;
        }
        #headbuttons {
            grid-row: 1;
            grid-column: 2;
            margin: 0 0.5rem;
        }
        sl-tab-group::part(tabs) {
            border-color: #ffffff22;
        }
        sl-tab::part(base) {
            color: var(--panel-fgcolor);
            opacity: 0.5;
        }
        sl-tab[active]::part(base) {
            opacity: 1.0;
        }
        .headlabel {
            margin: 0.5rem;
        }
        .footerlabel {
            font-size: 0.8rem;
            color: #b4d1ff;
        }
        #mapgeo {
            width: 100%;
            height: 10rem;
        }
        #edtgeoradius {
            width: 10rem;
        }
        sl-input::part(suffix) {
            color: #000000cc;
        }
    </style>
    <div id="main">
        <span id="head"></span>
        <div id="headbuttons">
            <sl-button id="btnclose" size="small">Close search</sl-button>
            <sl-button id="btnexpand" size="small"><sl-icon id="icobtnexpand"></sl-icon></sl-button>
        </div>
        <div id="configpanel">
            <sl-tab-group id="maintabgroup">
                <sl-tab slot="nav" panel="deeply" active>deeply</sl-tab>
                <sl-tab slot="nav" panel="byname">by name</sl-tab>
                <sl-tab slot="nav" panel="bytag">by tag</sl-tab>
                <sl-tab slot="nav" panel="bygeo">geographically</sl-tab>
                <sl-tab-panel name="deeply">
                    <div class="headlabel">
                        Please enter a term to search for.
                    </div>
                    <sl-input id="edttermdeeply"></sl-input>
                </sl-tab-panel>
                <sl-tab-panel name="byname">
                    <div class="headlabel">
                        Please enter a file name piece to search for.
                    </div>
                    <sl-input id="edttermname"></sl-input>
                </sl-tab-panel>
                <sl-tab-panel name="bytag">
                    <div class="headlabel">
                        Please enter a tag to search for.
                    </div>
                    <sl-input id="edttermtag"></sl-input>
                </sl-tab-panel>
                <sl-tab-panel name="bygeo">
                    <div class="headlabel">
                        Please choose a geographical range to search for.
                    </div>
                    <piweb-map id="mapgeo" position="lat=50&lon=20" zoom-level="3"></piweb-map>
                    <div class="headlabel">
                        Please choose a search radius.
                    </div>
                    <sl-input id="edtgeoradius" value="5000"><div slot="suffix">meters</div></sl-input>
                </sl-tab-panel>
            </sl-tab-group>
            <div class="footerlabel">
                Use the <sl-icon name="chevron-down"></sl-icon> button above once you have entered your query.
            </div>
        </div>
    </div>
`;

/**
* A panel for configuring search.
*/
export class SearchPanel extends HTMLElement {

    constructor() {
        super();
        const self = this;
        this._changedtimeouthandle = undefined;
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(panelTemplate.content.cloneNode(true));
        this._main = this._shadow.getElementById("main");
        this._head = this._shadow.getElementById("head");
        this._maintabgroup = this._shadow.getElementById("maintabgroup");
        this._edttermdeeply = this._shadow.getElementById("edttermdeeply");
        this._edttermname = this._shadow.getElementById("edttermname");
        this._edttermtag = this._shadow.getElementById("edttermtag");
        this._mapgeo = this._shadow.getElementById("mapgeo");
        this._edtgeoradius = this._shadow.getElementById("edtgeoradius");
        this._btnexpand = this._shadow.getElementById("btnexpand");
        this._icobtnexpand = this._shadow.getElementById("icobtnexpand");
        this._btnclose = this._shadow.getElementById("btnclose");
        this._configpanel = this._shadow.getElementById("configpanel");
        this._btnexpand.addEventListener("click", () => {
            self.expanded = !self.expanded;
        });
        this._btnclose.addEventListener("click", () => {
            self.dispatchEvent(new CustomEvent("close", { detail: {}, bubbles: true }));
        });
        this._geomarker = undefined;
        this._mapgeo.addEventListener("locationpicked", (event) => {
            self._setGeoMarker(event.detail.location);
            self._changed();
        });
        this._maintabgroup.addEventListener("sl-tab-show", this._changed.bind(this));
        this._edttermdeeply.addEventListener("sl-input", this._changed.bind(this));
        this._edttermname.addEventListener("sl-input", this._changed.bind(this));
        this._edttermtag.addEventListener("sl-input", this._changed.bind(this));
        this._edtgeoradius.addEventListener("sl-input", this._changed.bind(this));
    }

    connectedCallback() {
        this._head.textContent = this.configShortDescription;
    }

    async _setGeoMarker(pos) {
        if (this._geomarker) {
            this._geomarker.remove();
            this._geomarker = undefined;
        }
        if (pos)
            this._geomarker = await this._mapgeo.addMarker(pos);
    }

    _changed() {
        const self = this;
        if (this._changedtimeouthandle)
            clearTimeout(this._changedtimeouthandle);
        this._changedtimeouthandle = setTimeout(() => {
            self._head.textContent = self.configShortDescription;
            self.dispatchEvent(new CustomEvent("changed", { detail: {}, bubbles: true }));
        }, 1000);
    }

    static get observedAttributes() {
        return ["expanded"];
    }

    get configShortDescription() {
        const config = this.configDict;
        if (config.mode === "deeply") {
            if (config.term)
                return `Search deeply by "${config.term}"`;
        }
        else if (config.mode === "byname") {
            if (config.term)
                return `Search for names like "${config.term}"`;
        }
        else if (config.mode === "bytag") {
            if (config.term)
                return `Search for tag "${config.term}"`;
        }
        else if (config.mode === "bygeo") {
            if (config.position)
                return "Search geographically";
        }
        else
            throw new Error(`Invalid mode: ${config.mode}`);
        return "Search";
    }

    get configDict() {
        let mode;
        for (const tab of this._maintabgroup.querySelectorAll("sl-tab")) {
            if (tab.hasAttribute("active")) { // when called early, it seems to work only by direct attribute access
                mode = tab.getAttribute("panel");
                break;
            }
        }
        const config = { mode: mode };
        if (mode === "deeply")
            config.term = this._edttermdeeply.value;
        else if (mode === "byname")
            config.term = this._edttermname.value;
        else if (mode === "bytag")
            config.term = this._edttermtag.value;
        else if (mode === "bygeo") {
            config.position = this._geomarker?.position?.toValueString() || "";
            config.radius = this._edtgeoradius.value;
        }
        else
            throw new Error(`Invalid mode: ${mode}`);
        return config;
    }

    set configDict(config) {
        if (config.mode === "deeply")
            this._edttermdeeply.value = config.term || "";
        else if (config.mode === "byname")
            this._edttermname.value = config.term || "";
        else if (config.mode === "bytag")
            this._edttermtag.value = config.term || "";
        else if (config.mode === "bygeo") {
            this._setGeoMarker(config.position);
            this._edtgeoradius.value = config.radius || this._edtgeoradius.value;
        }
        else
            throw new Error(`Invalid mode: ${config.mode}`);
        this._maintabgroup.show(config.mode);
    }

    /**
    * If to expand the config panel.
    */
    get expanded() {
        return this.hasAttribute("expanded");
    }

    set expanded(v) {
        if (v)
            this.setAttribute("expanded", v);
        else
            this.removeAttribute("expanded");
    }

    attributeChangedCallback(name, oldVal, newVal) {
        if (name === "expanded") {
            const expand = (newVal !== null);
            this._icobtnexpand.name = expand ? "chevron-down" : "chevron-right";
            this._main.classList[expand ? "add" : "remove"]("expanded");
        }
    }

}

customElements.define("lawwenda-searchpanel", SearchPanel);
