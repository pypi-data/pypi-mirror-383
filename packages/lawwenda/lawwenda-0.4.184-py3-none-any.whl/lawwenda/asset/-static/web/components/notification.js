/**
* @license
* SPDX-FileCopyrightText: © 2021 Josef Hahn
* SPDX-License-Identifier: AGPL-3.0-only
*/

import { baseStylesRef } from "../piweb/styling.js";

const notificationTemplate = document.createElement("template");
notificationTemplate.innerHTML = `
    ${baseStylesRef()}
    <style>
        :host {
            display: block;
            overflow: hidden;
        }
        #main {
            margin: 0.5rem;
            border-top: 0.125rem solid #ffffff44;
            padding-top: 0.25rem;
            color: #ffffffee;
        }
    </style>
    <div id="main">
        <slot></slot>
    </div>
`;

/**
* An entry in the notification area.
*/
export class Notification extends HTMLElement {

    constructor() {
        super();
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(notificationTemplate.content.cloneNode(true));
    }

    close() {
        if (this.parentNode)
            this.parentNode.removeChild(this);
    }

}

customElements.define("lawwenda-notification", Notification);

export function addNotification(elem) {
    const notification = document.createElement("lawwenda-notification");
    notification.appendChild(elem);
    document.getElementById("notificationarea").appendChild(notification);
    return notification;
}

const copymoveTemplate = document.createElement("template");
copymoveTemplate.innerHTML = `
    ${baseStylesRef()}
    <style>
        #label {
            color: #d5cfff;
            text-overflow: ellipsis;
            white-space: nowrap;
            overflow: hidden;
        }
    </style>
    <div>
        <div id="label"></div>
        Go to the destination and trigger:
        <sl-button id="btntohere" size="small" type="primary"></sl-button>
        <sl-button id="btncancel" size="small">Cancel</sl-button>
    </div>
`;

/**
* An entry in the notification area.
*/
export class CopyMoveNotificationPiece extends HTMLElement {

    constructor() {
        super();
        const self = this;
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(copymoveTemplate.content.cloneNode(true));
        this._btntohere = this._shadow.getElementById("btntohere");
        this._btncancel = this._shadow.getElementById("btncancel");
        this._label = this._shadow.getElementById("label");
        this._btntohere.addEventListener("click", () => {
            self.dispatchEvent(new CustomEvent("trigger", { bubbles: true, composed: true }));
        });
        this._btncancel.addEventListener("click", () => {
            self.dispatchEvent(new CustomEvent("cancel", { bubbles: true, composed: true }));
        });
    }

    static get observedAttributes() {
        return ["action", "label"];
    }

    /**
    * The action text.
    */
    get action() {
        return this.getAttribute("action");
    }

    set action(v) {
        this.setAttribute("action", v);
    }

    /**
    * The label text.
    */
    get label() {
        return this.getAttribute("label");
    }

    set label(v) {
        this.setAttribute("label", v);
    }

    attributeChangedCallback(name, oldVal, newVal) {
        if (name === "action")
            this._btntohere.textContent = newVal;
        else if (name === "label")
            this._label.textContent = this._label.title = newVal;
    }

}

customElements.define("lawwenda-notificationpiece-copymove", CopyMoveNotificationPiece);
