/**
* @license
* SPDX-FileCopyrightText: © 2018 Josef Hahn
* SPDX-License-Identifier: AGPL-3.0-only
*/

// IMPORTANT: THIS WIDGET USES 3RD PARTY LIBRARIES. THEY ARE BUNDLED HERE.
// SOME OF THEM MUST BE INCLUDED IN YOUR HTML AS WELL (SEE index.html). CHECK ALSO THEIR LICENSES!

import { baseStylesRef } from "./styling.js";

const numfmt = new Intl.NumberFormat(undefined, { style: "decimal", maximumFractionDigits: 4 });

export class MapPosition {

    constructor(lat, lon) {
        let auxargs = {};
        if (lat && lat.lat !== undefined) {
            lon = lat.lon;
            lat = lat.lat;
            auxargs = lat.auxargs || auxargs;
        }
        else if (lat && lon === undefined) {
            for (const [prmkey, prmvalue] of new URLSearchParams(lat).entries()) {
                if (prmkey === "lat")
                    lat = prmvalue;
                else if (prmkey === "lon")
                    lon = prmvalue;
                else
                    auxargs[prmkey] = prmvalue;
            }
        }
        this.auxargs = auxargs;
        lat = parseFloat(lat || 0);
        lon = parseFloat(lon || 0);
        this.lat = lat;
        lon = ((lon % 360) + 360) % 360;
        if (lon > 180)
            lon = lon - 360;
        this.lon = this.lng /* this is what leaflet uses */ = lon;
    }

    toValueString() {
        return new URLSearchParams(Object.assign({ lat: this.lat, lon: this.lon }, this.auxargs)).toString();
    }

    toString() {
        return numfmt.format(this.lat) + " ; " + numfmt.format(this.lon);
    }

    equals(b) {
        return b && b.lat === this.lat && b.lon === this.lon;
    }

}

class MapDecoration {

    constructor(llmarker) {
        this.llmarker = llmarker;
    }

    remove() {
        this.llmarker.remove();
    }

    get position() {
        const p = this.llmarker.getLatLng();
        return new MapPosition(p.lat, p.lng);
    }

}

export class MapMarker extends MapDecoration {

}

export class MapCircle extends MapDecoration {

}

const mapviewTemplate = document.createElement("template");
mapviewTemplate.innerHTML = `
    ${baseStylesRef()}
    <style>
        :host {
            display: block;
            position: relative;
        }
        #main {
            height: 100%;
            width: 100%;
            overflow: hidden;
            position: absolute;
        }
        .leaflet-pane img { /* workaround for some leaflet oddness (broken tiling) */
            position: absolute;
        }
        .leaflet-pane :not(.leaflet-tile-pane) svg,
        .leaflet-pane .leaflet-marker-pane img { /* workaround for another leaflet oddness */
            z-index: 999999;
        }
        .leaflet-marker-pane { /* workaround for another leaflet oddness */
            position: relative;
            z-index: 999999;
        }
    </style>
    <div id="main">
    </div>
`;

export class MapView extends HTMLElement {

    _loadLeafletScript(callback) {
        let llscript;
        if (window._leafletScript)
            llscript = window._leafletScript;
        else {
            const leafleturl = import.meta.url.substring(0, import.meta.url.lastIndexOf("/")) + "/3rdparty/leaflet";
            const llstyle = document.createElement("link");
            document.head.appendChild(llstyle);
            llstyle.rel = "stylesheet";
            llstyle.type = "text/css";
            llstyle.href = `${leafleturl}/leaflet.css`;
            llscript = document.createElement("script");
            document.head.appendChild(llscript);
            llscript.type = "text/javascript";
            llscript.src = `${leafleturl}/leaflet.js`;
            window._leafletScript = llscript;
        }
        if (llscript._loaded)
            callback();
        else
            llscript.addEventListener("load", () => {
                llscript._loaded = true;
                callback();
            });
    }

    constructor() {
        super();
        this._shadow = this.attachShadow({ mode: "open" });
        this._shadow.appendChild(mapviewTemplate.content.cloneNode(true));
        this._main = this._shadow.getElementById("main");
        this._zoomlevel = 12;
        this._position = new MapPosition();
        this._leaflet = undefined;
        this._leafletdiv = undefined;
    }

    static get observedAttributes() {
        return ["zoom-level", "position", "user-may-zoom", "user-may-move", "zoom-control-visible"];
    }

    /**
    * The zoom level.
    */
    get zoomLevel() {
        return this.getAttribute("zoom-level");
    }

    set zoomLevel(v) {
        this.setAttribute("zoom-level", v);
    }

    /**
    * The position to center.
    */
    get position() {
        return new MapPosition(this.getAttribute("position"));
    }

    set position(v) {
        this.setAttribute("position", new MapPosition(v).toValueString());
    }

    /**
    * If to allow the user to zoom in the map.
    */
    get userMayZoom() {
        return this.getAttribute("user-may-zoom") === "yes";
    }

    set userMayZoom(v) {
        this.setAttribute("user-may-zoom", v ? "yes" : "no");
    }

    /**
    * If to allow the user to move around in the map.
    */
    get userMayMove() {
        return this.getAttribute("user-may-move") === "yes";
    }

    set userMayMove(v) {
        this.setAttribute("user-may-move", v ? "yes" : "no");
    }

    /**
    * If to show zoom controls.
    */
    get zoomControlVisible() {
        return this.getAttribute("zoom-control-visible") === "yes";
    }

    set zoomControlVisible(v) {
        this.setAttribute("zoom-control-visible", v ? "yes" : "no");
    }

    attributeChangedCallback(name, oldVal, newVal) {
        if (name === "zoom-level") {
            this._zoomlevel = parseInt(newVal);
            if (this._leaflet)
                this._leaflet.setView(this._position, this._zoomlevel);
        }
        else if (name === "position") {
            this._position = newVal ? new MapPosition(newVal) : undefined;
            if (this._leaflet)
                this._leaflet.setView(this._position, this._zoomlevel);
        }
        else if (name === "user-may-zoom") {
            this._userMayZoom = newVal === "yes";
            this._populate();
        }
        else if (name === "user-may-move") {
            this._userMayMove = newVal === "yes";
            this._populate();
        }
        else if (name === "zoom-control-visible") {
            this._zoomControlVisible = newVal === "yes";
            this._populate();
        }
    }

    _populate() {
        const self = this;
        if (this._leaflet)
            this._leaflet.remove();
        this._main.innerHTML = "";
        const leaflet = window.L;
        if (!leaflet)
            return;
        const leafletopts = {
            attributionControl: false,
            zoomControl: this._zoomControlVisible,
            boxZoom: true,
            doubleClickZoom: true,
            scrollWheelZoom: true,
            touchZoom: true,
            keyboard: true,
            dragging: true
        };
        if (!this._userMayMove) {
            leafletopts.doubleClickZoom = "center";
            leafletopts.scrollWheelZoom = "center";
            leafletopts.touchZoom = "center";
            leafletopts.keyboard = false;
            leafletopts.dragging = false;
        }
        if (!this._userMayZoom) {
            leafletopts.zoomControl = false;
            leafletopts.boxZoom = false;
            leafletopts.doubleClickZoom = false;
            leafletopts.scrollWheelZoom = false;
            leafletopts.touchZoom = false;
            leafletopts.keyboard = false;
        }
        const omap = document.createElement("div");
        omap.style.width = "100%";
        omap.style.height = "100%";
        omap.style.position = "relative";
        this._main.appendChild(omap);
        this._leaflet = leaflet.map(omap, leafletopts);
        leaflet.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "Map data © <a href=\"http://openstreetmap.org\">OpenStreetMap</a> contributors"
        }).addTo(this._leaflet);
        this._leaflet.on("moveend", function (ev) {
            if (!self._userMayMove) {
                // the map seems to always move a bit while zooming
                if (!self._leaflet_movingback) {
                    self._leaflet_movingback = true;
                    self._leaflet.setView(self._position, self._zoomLevel);
                }
                else
                    self._leaflet_movingback = false;
            }
        });
        this._leaflet.on("click", function (ev) {
            self.dispatchEvent(new CustomEvent("locationpicked", {
                detail: { location: new MapPosition(ev.latlng.lat, ev.latlng.lng) }, bubbles: true, composed: true
            }));
        });
        this.position = this.position; /* eslint no-self-assign: "off" */
    }

    connectedCallback() {
        const self = this;
        for (const [attname, defaultval] of [
            ["position", "lon=0&lat=0"],
            ["zoom-level", 12],
            ["user-may-zoom", "yes"],
            ["user-may-move", "yes"],
            ["zoom-control-visible", "yes"]
        ])
            if (!this.hasAttribute(attname))
                this.setAttribute(attname, defaultval);
        for (let i = 0; i < 5; i++) // really a shitty hack, yes
            setTimeout(async () => {
                (await self._getLeaflet()).invalidateSize();
            }, 500 * i);
    }

    async _getLeaflet() {
        const self = this;
        return new Promise((resolve, reject) => {
            self._loadLeafletScript(() => {
                if (!self._leaflet)
                    self._populate();
                resolve(self._leaflet);
            });
        });
    }

    async fitBounds(p1, p2) {
        const leaflet = await this._getLeaflet();
        leaflet.fitBounds([new MapPosition(p1), new MapPosition(p2)]);
    }

    async addMarker(position, config) {
        const leaflet = await this._getLeaflet();
        const llmarker = window.L.marker(new MapPosition(position), { title: config?.title || "" }).addTo(leaflet);
        return new MapMarker(llmarker);
    }

    async addCircle(position, config) {
        const leaflet = await this._getLeaflet();
        const llcircle = window.L.circle(new MapPosition(position), { radius: config?.radius || 1000 }).addTo(leaflet);
        return new MapCircle(llcircle);
    }

}

customElements.define("piweb-map", MapView);
