/**
* @license
* SPDX-FileCopyrightText: © 2021 Josef Hahn
* SPDX-License-Identifier: AGPL-3.0-only
*/

import { animateNode } from "./animation.js";
import { baseStylesRef } from "./styling.js";

const busyanimationTemplate = document.createElement("template");
busyanimationTemplate.innerHTML = `
    ${baseStylesRef()}
    <style>
        #main {
            position: relative;
            width: 100%;
            height: 100%;
        }
        #surface1 { /* TODO style nicer, bit more saturated colors */
            background-image: linear-gradient(70deg, #d2dfed 0%,#c8d7eb 26%,#a6c0e3 38%,#bed0ea 51%,#afc7e8 62%,
                                              #bad0ef 75%,#99b5db 88%,#799bc8 100%);
            animation: piweb_busysurfaceanimation 12s ease infinite;
        }
        #surface2 {
            background-image: linear-gradient(80deg, #e2e2e2 0%,#d3d3d3 20%,#c6c6c6 23%,#dbdbdb 50%,#c6c6c6 51%,
                                              #e5e5e5 69%,#c6c6c6 71%,#fefefe 100%);
            animation: piweb_busysurfaceanimation 10s ease infinite;
        }
        #surface3 {
            background-image: linear-gradient(70deg, #b7deed 0%,#48bfea 41%,#b7deed 43%,#71ceef 50%,#21b4e2 51%,
                                              #b7deed 58%,#75bdea 60%,#b7deed 66%,#b7deed 68%,#b7deed 100%);
            animation: piweb_busysurfaceanimation 8s ease infinite;
        }
        .surface {
            position: absolute;
            top: 0;
            left: 0;
            bottom: 0;
            right: 0;
            opacity: 0.2;
            background-size: 300% 300%;
            cursor: wait;
        }
        @keyframes piweb_busysurfaceanimation {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }
    </style>
    <div id="main">
        <div class="surface" id="surface1"></div>
        <div class="surface" id="surface2"></div>
        <div class="surface" id="surface3"></div>
    </div>
`;

/**
* Busy animation.
*/
export class BusyAnimation extends HTMLElement {

    constructor() {
        super();
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(busyanimationTemplate.content.cloneNode(true));
    }

}

customElements.define("piweb-busy", BusyAnimation);

class BusyControllerToken {

    constructor(controller) {
        this._controller = controller;
    }

    unset() {
        this._controller._unsetBusyToken(this);
    }

}

export class BusyController {

    constructor() {
        this._tokens = [];
    }

    _stateChanged(isBusy) {
        throw new Error("not implemented");
    }

    setBusy() {
        // return;//TODO xx
        const token = new BusyControllerToken(this);
        if (this._tokens.length === 0)
            this._stateChanged(true);
        this._tokens.push(token);
        return token;
    }

    unsetBusy() {
        // return;//TODO xx
        if (this._tokens.length > 0)
            this._stateChanged(false);
        this._tokens = [];
    }

    _unsetBusyToken(token) {
        const itoken = this._tokens.indexOf(token);
        if (itoken === -1)
            return;
        this._tokens.splice(itoken, 1);
        if (this._tokens.length === 0)
            this._stateChanged(false);
    }

}

export class BusyElementController extends BusyController {

    constructor(element, fadeInAnimationName, fadeOutAnimationName) {
        super();
        this._element = element;
        this._fadeInAnimationName = fadeInAnimationName;
        this._fadeOutAnimationName = fadeOutAnimationName;
        this._busyanim = undefined;
    }

    _stateChanged(isBusy) {
        /* eslint no-unreachable: "off" */ // TODO xx
        return; // TODO xx
        const animationDuration = getComputedStyle(document.body).getPropertyValue("--sl-transition-normal");
        if (isBusy) {
            this._busyanim = document.createElement("piweb-busy");
            this._busyanim.style.position = "absolute";
            this._busyanim.style.top = 0;
            this._busyanim.style.left = 0;
            this._busyanim.style.bottom = 0;
            this._busyanim.style.right = 0;
            this._busyanim.style.opacity = 0;
            this._busyanim.style.animationFillMode = "forwards";
            this._busyanim.style.animationDuration = animationDuration;
            this._busyanim.style.animationName = this._fadeInAnimationName;
            this._element.appendChild(this._busyanim);
        }
        else {
            const busyanim = this._busyanim;
            (async () => {
                busyanim.style.opacity = window.getComputedStyle(busyanim).opacity;
                await animateNode(busyanim, this._fadeOutAnimationName, animationDuration);
                busyanim.parentNode.removeChild(busyanim);
            })();
            this._busyanim = undefined;
        }
    }

}
