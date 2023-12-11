import {
    getStorageLocal,
    setStorageLocal,
    parseUrl,
    getUrlByInfo,
    generateClientId,
    syncUrl,
    jsonParse
} from "./common/utils";
import * as querystring from "querystring";
import {Howl} from 'howler'
import Recorder from './common/recorder'
import Ws from './common/ws'

const urlMap = {}
const obj = {
    ws: null,
    wsUrl: '',
    clientId: '',
    soundQueue: [],
    player: null
}

async function main() {
    chrome.contentSettings.microphone.set({
        primaryPattern: "*://".concat(chrome.runtime.id, "/*"),
        setting: "allow"
    })
    const storage = await getStorageLocal({
        clientId: ''
    })
    if (!storage || !storage.clientId) {
        const res = await generateClientId()
        if (!res || res.code !== 0 || !res.data) {
            return
        }
        obj.clientId = res.data
    } else {
        obj.clientId = storage.clientId
    }
    await setStorageLocal({clientId: obj.clientId})
    obj.wsUrl = `ws://localhost:8089/hapi/ws/${obj.clientId}`

    if (obj.ws) {
        obj.ws.close()
    }
    obj.ws = new Ws(obj.wsUrl)
    obj.ws.onopen(e => {
    })
    obj.ws.onmessage(async e => {
        if (e.data) {
            if (e.data === 'pong') {
                return
            }
            const res = jsonParse(e.data || '')
            if (!res) {
                return
            }
            if (res && res.data) {
                obj.soundQueue.push(res.data)
            }
        }
    })

    obj.ws.onerror(async e => {
        console.log('onerror')
    })

    obj.ws.onclose(async e => {
        console.log('onclose')
    })
    obj.ws.connect(100)

    const recorder = new Recorder(() => {
        recorder.start()
        setTimeout(() => {
            recorder.stop()
        }, 3000)
    }, data => {
        if (obj.ws) {
            obj.ws.send(JSON.stringify({
                action: 'test',
                data: data
            }))
        }
    })

    // setTimeout(() => {
    //     debugger
    //     for (let tabId in urlMap) {
    //         if (urlMap[tabId] && urlMap[tabId].pUrl) {
    //             sendMessage(tabId, {
    //                 action: 'getSeek'
    //             })
    //         }
    //     }
    // }, 5000)
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        sendResponse({code: 0})
        debugger
        if (message.action === 'getSeek') {
            if (urlMap[sender.tab.id] && urlMap[sender.tab.id].url) {
                const u = parseUrl(sender.url)
                if (u && u.hostname && u.hostname.includes("youtube.com")) {
                    const o = querystring.parse(u.search.replace(/^\?/, ''))
                    let pUrl = getUrlByInfo(sender.url, {
                        host: true,
                        pathname: true,
                        port: true,
                        hash: false,
                        protocol: true,
                        search: false
                    })
                    if (pUrl && o.v) {
                        pUrl = pUrl.replace(/\/$/, '')
                        pUrl += '?v=' + o.v
                    }
                    urlMap[sender.tab.id] = {
                        pUrl,
                        url: sender.url,
                        curl: u,
                        time: message.data,
                        videoId: o.v || ''
                    }
                }
            }
        }
    });
    chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
        if (tabId && tab.url) {
            const u = parseUrl(tab.url)
            if (u && u.hostname && u.hostname.includes("youtube.com")) {
                const o = querystring.parse(u.search.replace(/^\?/, ''))
                let pUrl = getUrlByInfo(tab.url, {
                    host: true,
                    pathname: true,
                    port: true,
                    hash: false,
                    protocol: true,
                    search: false
                })
                if (pUrl && o.v) {
                    pUrl = pUrl.replace(/\/$/, '')
                    pUrl += '?v=' + o.v
                }
                if (pUrl && o.v && (!urlMap[tabId] || !urlMap[tabId].sync)) {
                    if (!urlMap[tabId]) {
                        urlMap[tabId] = {
                            sync: true
                        }
                    }
                    await syncUrl(pUrl, obj.clientId)
                }
                urlMap[tabId] = {
                    pUrl,
                    url: tab.url,
                    curl: u,
                    time: 0,
                    videoId: o.v || '',
                    sync: true
                }
            }

        }
    });

    chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
        if (tabId && urlMap[tabId]) {
            delete urlMap[tabId]
        }
    });

    while (true) {
        const data = obj.soundQueue.shift()
        if (!data) {
            await new Promise(resolve => {
                setTimeout(() => {
                    resolve()
                }, 1000)
            })
            continue
        }
        obj.player = new Howl({
            src: [data]
        });
        obj.player.play();
        await new Promise(resolve => {
            obj.player.onplayerror = function () {
                console.log('播放失败', data);
                resolve()
            }
            obj.player.on('end', () => {
                console.log('播放完成', data);
                resolve()
            })
        })
    }
}

main()