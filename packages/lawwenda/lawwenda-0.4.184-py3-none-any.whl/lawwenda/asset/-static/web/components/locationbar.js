/**
* @license
* SPDX-FileCopyrightText: © 2021 Josef Hahn
* SPDX-License-Identifier: AGPL-3.0-only
*/

import { baseStylesRef } from "../piweb/styling.js";

const barTemplate = document.createElement("template");
barTemplate.innerHTML = `
    ${baseStylesRef()}
    <style>
        :host {
            display: block;
            overflow: hidden;
        }
        #pieces {
            display: grid;
            column-gap: 0.5em;
            grid-auto-columns: max-content;
            margin-left: 0.5em;
        }
        .btnsegment {
            overflow: hidden;
            text-overflow: ellipsis;
            text-align: center;
            min-width: 2em;
            height: 2em;
            border-bottom: 0.25em solid #ffffff66;
            color: #ffffff91;
            grid-row: 1;
            cursor: default;
            transition: color 0.5s, border-color 0.5s;
        }
        .btnsegment:hover {
            color: #ffffffaa;
            border-color: #ffffffaa;
        }
    </style>
    <div id="pieces">
    </div>
`;

/**
* A bar that shows a button for each segment of a path.
*/
export class LocationBar extends HTMLElement {

    constructor() {
        super();
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(barTemplate.content.cloneNode(true));
        this._pieces = this._shadow.getElementById("pieces");
        this._path = "";
    }

    static get observedAttributes() {
        return ["path"];
    }

    /**
    * The path to show.
    */
    get path() {
        return this.getAttribute("path");
    }

    set path(v) {
        this.setAttribute("path", v);
    }

    attributeChangedCallback(name, oldVal, newVal) {
        if (name === "path") {
            this._path = newVal;
            this._populate();
        }
    }

    _populate() {
        const self = this;
        this._pieces.innerHTML = "";
        const pathsegments = ["/"];
        for (const pathsegment of this._path.split("/")) {
            if (pathsegment)
                pathsegments.push(`${pathsegment}/`);
        }
        let path = "";
        for (const pathsegment of pathsegments) {
            path += pathsegment;
            const btnsegment = document.createElement("div");
            btnsegment.className = "btnsegment";
            btnsegment.textContent = pathsegment;
            btnsegment.addEventListener("click", ((p) => {
                return () => {
                    self.dispatchEvent(new CustomEvent("pathSelected", { detail: { path: p }, bubbles: true }));
                };
            })(path));
            this._pieces.appendChild(btnsegment);
        }
    }

}

customElements.define("lawwenda-locationbar", LocationBar);
