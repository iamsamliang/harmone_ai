import axios from "axios";

const API_URL = 'http://localhost:8089/hapi';
axios.defaults.baseURL = API_URL;

export async function sleep(t) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            resolve()
        }, t)
    })
}

export function jsonParse(str, flag = false) {
    if (typeof str !== 'string') {
        if (typeof str === 'object') {
            return str
        }
        return flag ? [] : {}
    }
    let res = flag ? [] : {}
    try {
        res = JSON.parse(str)
    } catch (e) {
        res = flag ? [] : {}
    }
    return res
}

export function jsonStringify(o, deep = false) {
    if (typeof o !== 'object') {
        if (typeof o === 'string') {
            return o
        }
        return ''
    }
    if (deep) {
        o = f(o)
    }

    let res = ''
    try {
        res = JSON.stringify(o)
    } catch (e) {
        debugger;

        _log('jsonStringify', e)
        res = ''
    }
    return res
}

export async function generateClientId() {
    const res = await axios.request({
        method: 'get',
        url: `/client_id`
    }).catch(e => {
        console.log(e)
        return null
    })
    return res?.data || null
}

export async function syncUrl(url, clientId) {
    if (!url || typeof url !== 'string' || !clientId || typeof clientId !== 'string') {
        return null
    }
    const res = await axios.request({
        method: 'post',
        url: `/url`,
        data: {
            "yt_url": url,
            "client_id": clientId
        }
    }).catch(e => {
        console.log(e)
        return null
    })
    return res?.data || null
}

export function getStorageLocal(o = {}, callback) {
    return new Promise((resolve, reject) => {
        chrome.storage.local.get(o, items => {
            if (typeof callback === 'function') {
                callback(items)
            }
            resolve(items)
        });
    }).catch(e => {
        return null
    })
}

export function setStorageLocal(o = {}, callback) {
    return new Promise((resolve, reject) => {
        chrome.storage.local.set({
            ...o
        }, () => {
            if (typeof callback === 'function') {
                callback(true)
            }
            resolve(true)
        });
    }).catch(e => {
        return null
    })
}

export function parseUrl(url) {
    if (!url) {
        return false
    }
    try {
        const u = new URL(url)
        return u
    } catch (e) {
        return null
    }
}

export function getUrlByInfo(url, {
    host = true,
    pathname = true,
    port = true,
    hash = false,
    protocol = true,
    search = false
} = {
    host: true,
    pathname: true,
    port: true,
    hash: false,
    protocol: true,
    search: false
}) {
    if (!url || typeof url !== 'string') {
        return ''
    }
    const u = parseUrl(url)
    if (!u || !u.host) {
        return ''
    }

    let ret = ''

    if (protocol) {
        ret += u.protocol + (/:$/.test(u.protocol) ? '//' : '://')
    }
    if (host) {
        ret += u.hostname
    }
    if ((port && u.port) || u.port) {
        ret += ':' + u.port
    }
    if (pathname) {
        ret += /\/$/.test(u.pathname) ? u.pathname : (u.pathname + '/')
    }
    if (hash) {
        ret += u.hash
    }
    if (search) {
        ret += u.search
    }
    return ret
}

export function sendMessage(tabId, message, callback) {
    tabId = parseInt(tabId)
    if (isNaN(tabId) || tabId < 0) {
        return
    }
    chrome.tabs.sendMessage(tabId, message, response => {
        if (chrome.runtime.lastError) {
            console.log(chrome.runtime.lastError);
            return
        }
        if (callback && typeof callback === 'function') {
            callback(response)
        }
    })
}