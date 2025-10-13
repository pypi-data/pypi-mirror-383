/**
* @license
* SPDX-FileCopyrightText: © 2021 Josef Hahn
* SPDX-License-Identifier: AGPL-3.0-only
*/

/**
* Animates a DOM node.
*/
export async function animateNode(node, animationname, animationduration) {
    animationduration = animationduration || getComputedStyle(document.body).getPropertyValue("--sl-transition-slow");
    if (node.style.animationName === animationname) {
        node.style.animationName = "";
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                animateNode(node, animationname, animationduration).then(resolve, reject);
            });
        });
    }
    else
        return new Promise((resolve, reject) => {
            const curreq = node._curreq = new Object();
            function _animationended() {
                node.removeEventListener("animationend", _animationended);
                if (curreq === node._curreq) {
                    node.style.animationName = "";
                    resolve(true);
                }
                else
                    resolve(false);
            }
            node.addEventListener("animationend", _animationended);
            node.style.animationDuration = animationduration;
            node.style.animationFillMode = "forwards";
            node.style.animationName = animationname;
        });
}
