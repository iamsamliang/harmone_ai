import {sleep} from "./utils";

export default class Ws {
    constructor(url, open, message, error, close) {
        this.status = 0
        this.ws = null
        this.queue = []
        this.url = url
        this.time = 100
        this.openFn = e => {
            if (open && typeof open === 'function') {
                open(e)
            }
            if (this.queue && Array.isArray(this.queue) && this.queue.length) {
                let message = this.queue.shift()
                while (message) {
                    this.send(message)
                    message = this.queue.shift()
                }
            }
        }
        this.messageFn = e => {
            if (message && typeof message === 'function') {
                message(e)
            }
        }
        this.errorFn = e => {
            if (error && typeof error === 'function') {
                error(e)
            }
        }
        this.closeFn = e => {
            if (close && typeof close === 'function') {
                close(e)
            }
        }
    }

    send(message) {
        if (!this.ws) {
            this.queue.push(message)
        } else if (this.ws.readyState === this.ws.CONNECTING) {
            this.queue.push(message)
        } else if (this.ws.readyState === this.ws.OPEN) {
            this.ws.send(message)
        } else if (this.ws.readyState === this.ws.CLOSING) {
            this.queue.push(message)
        } else if (this.ws.readyState === this.ws.CLOSED) {
            this.queue.push(message)
        }
    }

    connect(time) {
        if (!time) {
            if (typeof this.time !== 'number' || (this.time > 1000 && this.time < 100)) {
                this.time = 100
            }
        } else if (typeof time !== 'number' || (time > 1000 && time < 100)) {
            this.time = 100
        } else {
            this.time = time
        }
        try {
            this.ws = new WebSocket(this.url)
            if (!this.ws) {
                return this.ws
            }
            if (this.ws.readyState !== this.ws.CONNECTING) {
                this.close()
                return this.ws
            }
            this.ws.addEventListener('open', this.openFn)
            this.ws.addEventListener('message', this.messageFn)
            this.ws.addEventListener('error', this.errorFn)
            this.ws.addEventListener('close', this.closeFn)
            return this.ws
        } catch (e) {
            this.close()
        }
        return this.ws
    }

    close() {
        if (this.ws && typeof this.ws.close === 'function') {
            this.ws.close()
        }
        this.ws = null
    }

    onopen(cb) {
        this.openFn = e => {
            if (cb && typeof cb === 'function') {
                cb(e)
            }
            if (this.queue && Array.isArray(this.queue) && this.queue.length) {
                let message = this.queue.shift()
                while (message) {
                    this.send(message)
                    message = this.queue.shift()
                }
            }
        }
    }

    async onerror(cb) {
        this.errorFn = e => {
            if (cb && typeof cb === 'function') {
                cb(e)
            }
        }
    }

    async onmessage(cb) {
        this.messageFn = e => {
            if (cb && typeof cb === 'function') {
                cb(e)
            }
        }
    }

    async onclose(cb) {
        this.closeFn = async e => {
            if (cb && typeof cb === 'function') {
                cb(e)
            }
            await sleep(100)
            if (this.ws && this.ws.removeEventListener) {
                this.ws.removeEventListener('open', this.openFn)
                this.ws.removeEventListener('message', this.messageFn)
                this.ws.removeEventListener('error', this.errorFn)
                this.ws.removeEventListener('close', this.closeFn)
                this.close()
            }
            this.connect(this.time)
        }
    }
}