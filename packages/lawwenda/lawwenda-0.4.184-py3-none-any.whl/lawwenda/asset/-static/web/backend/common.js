/**
* @license
* SPDX-FileCopyrightText: © 2021 Josef Hahn
* SPDX-License-Identifier: AGPL-3.0-only
*/

import { ajax } from "../piweb/comm.js";

export const urlInternalsName = document.body.getAttribute("data-url-internals-name");

const csrf_token = document.body.getAttribute("data-csrf_token");

async function lawwendaAjax(cfg) {
    const headers = cfg.headers = cfg.headers || {};
    headers["X-CSRFToken"] = csrf_token;
    cfg.url = `${urlInternalsName}/api/${cfg.url}`;
    return ajax(cfg);
}

/**
* Low-level backend functions.
*
* For some features there are higher-level facilities.
*/
class Backend {

    /**
    * Returns content of a directory.
    */
    async listDirectoryEntries(path, config) {
        const dirdata = await lawwendaAjax({
            url: "dir/",
            data: {
                path: path,
                config: JSON.stringify(config || {})
            }
        });
        const result = [];
        for (const entrydata of dirdata)
            result.push(this._prepareEntry(entrydata));
        return result;
    }

    /**
    * Returns details for a file or directory.
    */
    async entryDetails(path) {
        const result = await lawwendaAjax({
            url: "details/",
            data: {
                path: path
            }
        });
        return this._prepareEntry(result);
    }

    /**
    * Deletes a file or directory from the disk.
    */
    async deleteEntries(paths) {
        return lawwendaAjax({
            url: "delete/",
            method: "POST",
            data: {
                paths: paths
            }
        });
    }

    /**
    * Creates a directory.
    */
    async createDirectory(path) {
        return lawwendaAjax({
            url: "mkdir/",
            method: "POST",
            data: {
                path: path
            }
        });
    }

    /**
    * Renames a file or directory.
    */
    async renameEntry(path, newname) {
        return lawwendaAjax({
            url: "rename/",
            method: "POST",
            data: {
                path: path,
                newname: newname
            }
        });
    }

    /**
    * Sets the comment for some files or directories.
    */
    async commentEntries(paths, comment) {
        return lawwendaAjax({
            url: "set_comment/",
            method: "POST",
            data: {
                paths: paths,
                comment: comment
            }
        });
    }

    /**
    * Sets the rating for a some files or directories.
    */
    async rateEntries(paths, rating) {
        return lawwendaAjax({
            url: "set_rating/",
            method: "POST",
            data: {
                paths: paths,
                rating: rating
            }
        });
    }

    /**
    * Sets the geo location for some files or directories.
    */
    async setEntriesGeo(paths, geo) {
        return lawwendaAjax({
            url: "set_geo/",
            method: "POST",
            data: {
                paths: paths,
                geo: geo
            }
        });
    }

    /**
    * Returns all known tags.
    */
    async knownTags() {
        return lawwendaAjax({ url: "known_tags/" });
    }

    /**
    * Removes a tag from some files or directories.
    */
    async removeTagFromEntries(paths, tag) {
        return lawwendaAjax({
            url: "untag_entries/",
            method: "POST",
            data: {
                paths: paths,
                tag: tag
            }
        });
    }

    /**
    * Adds a tag to some files or directories.
    */
    async addTagToEntries(paths, tag) {
        return lawwendaAjax({
            url: "tag_entries/",
            method: "POST",
            data: {
                paths: paths,
                tag: tag
            }
        });
    }

    /**
    * Adds a tag to some files or directories.
    */
    async upload(files, destpath) {
        if (files.length === 0)
            return;
        const fd = new FormData();
        fd.set("destpath", destpath);
        for (const file of files)
            fd.append("upload", file);
        return lawwendaAjax({
            url: "upload/",
            method: "POST",
            data: fd
        });
    }

    /**
    * Copies some files or directories to another directory.
    */
    async copyEntries(srcpaths, destpath) {
        return lawwendaAjax({
            url: "copy/",
            method: "POST",
            data: {
                srcpaths: srcpaths,
                destpath: destpath
            }
        });
    }

    /**
    * Moves some files or directories to another directory.
    */
    async moveEntries(srcpaths, destpath) {
        return lawwendaAjax({
            url: "move/",
            method: "POST",
            data: {
                srcpaths: srcpaths,
                destpath: destpath
            }
        });
    }

    /**
    * Returns a url for downloading some files or directories as zip file.
    */
    async zipEntries(paths) {
        const result = await lawwendaAjax({
            url: "zip/",
            method: "POST",
            data: {
                paths: paths
            }
        });
        return result.url;
    }

    _prepareEntry(entry) {
        entry.path = sanitizePath(`${entry.dirpath}/${entry.name}`);
        return entry;
    }

}

/**
* The Backend.
*/
export const backend = new Backend();

/**
* Brings a path in a sane normalized form.
*/
export function sanitizePath(p) {
    let pp;
    do {
        pp = p;
        p = p.replace("//", "/");
    }
    while (p !== pp);
    while (p.startsWith("/"))
        p = p.substring(1);
    while (p.endsWith("/"))
        p = p.substring(0, p.length - 1);
    return p;
}

export function relativePathByRefPath(path, refpath) {
    const pathpieces = path.split("/").filter(x => x);
    const refpathpieces = refpath.split("/").filter(x => x);
    const resultpieces = [];
    while (pathpieces.length > 0 && refpathpieces.length > 0 && pathpieces[0] === refpathpieces[0]) {
        pathpieces.splice(0, 1);
        refpathpieces.splice(0, 1);
    }
    while (refpathpieces.length > 0) {
        resultpieces.push("..");
        refpathpieces.splice(0, 1);
    }
    for (const pathpiece of pathpieces)
        resultpieces.push(pathpiece);
    return resultpieces.join("/");
}

/**
* Returns the thumbnail url for a path.
*/
export function getThumbnailUrl(p) {
    return `${urlInternalsName}/api/thumbnail/?path=${encodeURIComponent(p)}`;
}
