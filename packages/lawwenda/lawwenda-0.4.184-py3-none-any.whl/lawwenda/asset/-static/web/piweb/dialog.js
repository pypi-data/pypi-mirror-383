/**
* @license
* SPDX-FileCopyrightText: © 2021 Josef Hahn
* SPDX-License-Identifier: AGPL-3.0-only
*/

/**
* Shows a dialog.
*/
export function showShoelaceDialog(dialogName) {
    const dialog = document.createElement(dialogName);
    document.body.appendChild(dialog);
    dialog._dialog.addEventListener("sl-after-hide", (event) => {
        if (event.target === dialog._dialog)
            document.body.removeChild(dialog);
    });
    dialog._dialog.show();
    return dialog;
}
