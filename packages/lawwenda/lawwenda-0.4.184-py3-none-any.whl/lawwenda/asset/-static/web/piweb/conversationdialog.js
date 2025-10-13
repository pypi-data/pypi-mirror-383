/**
* @license
* SPDX-FileCopyrightText: © 2021 Josef Hahn
* SPDX-License-Identifier: AGPL-3.0-only
*/

import { baseStylesRef } from "./styling.js";
import { showShoelaceDialog } from "./dialog.js";

const dialogTemplate = document.createElement("template");
dialogTemplate.innerHTML = `
    ${baseStylesRef()}
    <style>
        ::slotted(sl-button) {
            margin: var(--sl-spacing-medium);
        }
        #lblmessage {
            margin: var(--sl-spacing-medium) 0 var(--sl-spacing-x-large) 0;
            white-space: pre-wrap;
        }
    </style>
    <sl-dialog no-header>
        <div id="lblmessage"></div>
        <slot name="footer" slot="footer"></slot>
    </sl-dialog>
`;

/**
* Base for all kinds of conversation dialogs. See the functions in this module.
*/
export class ConversationDialog extends HTMLElement {

    constructor() {
        super();
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(dialogTemplate.content.cloneNode(true));
        this._dialog = this._shadow.querySelector("sl-dialog");
        this._lblmessage = this._shadow.getElementById("lblmessage");
    }

    static get observedAttributes() {
        return ["message"];
    }

    /**
    * The dialog message text.
    */
    get message() {
        return this.getAttribute("message");
    }

    set message(v) {
        this.setAttribute("message", v);
    }

    attributeChangedCallback(name, oldVal, newVal) {
        if (name === "message")
            this._lblmessage.textContent = newVal;
    }

}

customElements.define("piweb-conversationdialog", ConversationDialog);

/**
* Shows a message dialog (a message text and some buttons).
*/
export async function messageDialog(cfg) {
    return new Promise((resolve, reject) => {
        const dialog = showShoelaceDialog("piweb-conversationdialog");
        dialog.message = cfg.message;
        if (!cfg.buttons) {
            cfg.buttons = ["OK"];
            cfg.defaultAcceptAnswer = cfg.defaultCancelAnswer = 0;
        }
        for (const ibutton in cfg.buttons) {
            const btn = document.createElement("sl-button");
            btn.slot = "footer";
            btn.type = "primary";
            btn.textContent = cfg.buttons[ibutton];
            btn._dialogresult = parseInt(ibutton);
            dialog.appendChild(btn);
        }
        function closeDialog(dialogresult) {
            resolve(dialogresult);
            dialog.removeEventListener("sl-hide", _preventHide);
            dialog._dialog.hide();
        }
        const _preventHide = (event) => {
            event.preventDefault();
            if (cfg.defaultCancelAnswer !== undefined)
                closeDialog(cfg.defaultCancelAnswer);
        };
        dialog.addEventListener("sl-hide", _preventHide);
        dialog._dialog.addEventListener("click", (event) => {
            const dialogresult = event.target._dialogresult;
            if (dialogresult !== undefined) {
                closeDialog(dialogresult);
                event.stopImmediatePropagation();
            }
        });
        if (cfg.contentnodes?.length > 0) {
            for (const contentnode of cfg.contentnodes)
                dialog._dialog.appendChild(contentnode);
            dialog.addEventListener("sl-after-show", () => {
                (cfg.contentnodes[0].setFocus || cfg.contentnodes[0].focus).call(cfg.contentnodes[0]);
            }, { once: true });
        }
        dialog.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === "Escape") {
                const keyanswer = cfg[(event.key === "Enter") ? "defaultAcceptAnswer" : "defaultCancelAnswer"];
                if (keyanswer !== undefined)
                    closeDialog(keyanswer);
            }
        });
    });
}

/**
* Shows an input dialog (a question text, a text input field, and some buttons).
*/
export async function confirmationYesNoMessageDialog(cfg) {
    return (await messageDialog(Object.assign({
        buttons: ["No", "Yes"],
        defaultCancelAnswer: 0,
        defaultAcceptAnswer: 1
    }, cfg))) === 1;
}

/**
* Shows an input dialog (a question text, a text input field, and some buttons).
*/
export async function inputDialog(cfg) {
    const edt = document.createElement("sl-input");
    edt.value = cfg.defaultAnswer || "";
    cfg.contentnodes = [edt, ...(cfg.contentnodes || [])];
    cfg.buttons = ["Cancel", "OK"];
    cfg.defaultCancelAnswer = 0;
    cfg.defaultAcceptAnswer = 1;
    if ((await messageDialog(cfg)) === 1)
        return edt.value;
}

/**
* Shows a choice dialog (a question text and a list of choices to select from).
*/
export async function choiceDialog(cfg) {
    const menu = document.createElement("div");
    menu.className = "ginger-vertical-menu";
    for (const ichoice in cfg.choices) {
        const menuitem = document.createElement("sl-button");
        menuitem.textContent = cfg.choices[ichoice];
        menuitem._dialogresult = parseInt(ichoice) + 1;
        menu.appendChild(menuitem);
    }
    cfg.contentnodes = [menu, ...(cfg.contentnodes || [])];
    cfg.buttons = ["Cancel"];
    cfg.defaultCancelAnswer = 0;
    const result = await messageDialog(cfg);
    if (result)
        return result - 1;
}
