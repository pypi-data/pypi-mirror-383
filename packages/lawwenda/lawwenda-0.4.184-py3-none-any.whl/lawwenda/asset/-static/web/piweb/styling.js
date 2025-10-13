/**
* @license
* SPDX-FileCopyrightText: © 2021 Josef Hahn
* SPDX-License-Identifier: AGPL-3.0-only
*/

/**
* Returns a html snippet that includes the base css styling, e.g. for inside shadow dom of web components.
*/
export function baseStylesRef() {
    if (window.piwebBaseStylesRef === undefined)
        throw new Error("window._piwebBaseStylesRef is unset (must be set early by a script snippet on app side).");
    return window.piwebBaseStylesRef;
}
