import Recorde from 'js-audio-recorder';
import Recorder from 'recorder-core'
import 'recorder-core/src/engine/mp3'
import 'recorder-core/src/engine/mp3-engine'
import 'recorder-core/src/extensions/waveview'

class RecorderManager {
    constructor(cb, dataCb) {
        //顺带打一份wav的log，录音后执行mp3、wav合并的demo代码可对比音质
        this.chunks = [];
        this.testOutputWavLog = false;
        this.testSampleRate = 16000;
        this.testBitRate = 16;
        //发送间隔时长(毫秒)，mp3 chunk数据会缓冲，当pcm的累积时长达到这个时长，就会传输发送。这个值在takeoffEncodeChunk实现下，使用0也不会有性能上的影响。
        this.SendInterval = 300;
        this.dataCb = null
        if (dataCb && typeof dataCb === 'function') {
            this.dataCb = dataCb
        }
        //重置环境，每次开始录音时必须先调用此方法，清理环境
        this.realTimeSendTryTime = 0;
        this.realTimeSendTryNumber = 0;
        this.transferUploadNumberMax = 0;
        this.realTimeSendTryBytesChunks = [];
        this.realTimeSendTryClearPrevBufferIdx = 0;
        this.realTimeSendTryWavTestBuffers = [];
        this.realTimeSendTryWavTestSampleRate = 0;
        this.recorder = null
        Recorder.Destroy()
        const recorder = Recorder({
            type: "mp3",
            sampleRate: this.testSampleRate,
            bitRate: this.testBitRate,
            onProcess: (buffers, powerLevel, bufferDuration, bufferSampleRate, newBufferIdx, asyncEnd) => {
                // console.log('onProcess', buffers, powerLevel, bufferDuration, bufferSampleRate, newBufferIdx, asyncEnd)
                //实时数据处理，清理内存
                this.realTimeOnProcessClear(buffers, powerLevel, bufferDuration, bufferSampleRate, newBufferIdx, asyncEnd);
            },
            takeoffEncodeChunk: chunkBytes => {
                // console.log('takeoffEncodeChunk', chunkBytes)
                //接管实时转码，推入实时处理
                this.realTimeSendTry(chunkBytes, false);
            }
        });
        recorder.close();

        let start = 0
        recorder.open(() => {
            start++
            if (start > 1) {
                this.recorder = recorder
                if (cb && typeof cb === 'function') {
                    cb(recorder)
                }
            }
        }, () => {
            console.log('open error')
        })

        Recorde.getPermission().then(() => {
            start++
            if (start > 1) {
                this.recorder = recorder
                if (cb && typeof cb === 'function') {
                    cb(recorder)
                }
            }
        });
    }

    realTimeSendTryReset() {
        this.realTimeSendTryTime = 0;
    }

    //=====实时处理核心函数==========
    realTimeSendTry(chunkBytes, isClose) {
        //推入缓冲再说
        if (chunkBytes) {
            if (!this.realTimeSendTryBytesChunks || !this.realTimeSendTryBytesChunks.length) {
                this.realTimeSendTryBytesChunks = []
            }
            this.realTimeSendTryBytesChunks.push(chunkBytes);
            if (!this.chunks || !this.chunks.length) {
                this.chunks = []
            }
            this.chunks.push(chunkBytes)
        }

        const t1 = Date.now();
        if (!isClose && t1 - this.realTimeSendTryTime < this.SendInterval) {
            return;//控制缓冲达到指定间隔才进行传输
        }
        this.realTimeSendTryTime = t1;
        const number = ++this.realTimeSendTryNumber;

        //mp3缓冲的chunk拼接成一个更长点的mp3
        let len = 0;
        for (let i = 0; i < this.realTimeSendTryBytesChunks.length; i++) {
            len += this.realTimeSendTryBytesChunks[i].length;
        }
        const chunkData = new Uint8Array(len);
        for (let i = 0, idx = 0; i < this.realTimeSendTryBytesChunks.length; i++) {
            const chunk = this.realTimeSendTryBytesChunks[i];
            chunkData.set(chunk, idx);
            idx += chunk.length;
        }
        this.realTimeSendTryBytesChunks = [];

        //推入传输
        let blob = null
        let meta = {};
        //mp3不是空的
        if (chunkData.length > 0) {
            blob = new Blob([chunkData], {type: "audio/mp3"});
            //读取出这个mp3片段信息
            meta = Recorder.mp3ReadMeta([chunkData.buffer], chunkData.length) || {};
        }
        this.transferUpload(number, blob, meta.duration || 0, {
            set: {
                type: "mp3",
                sampleRate: meta.sampleRate,
                bitRate: meta.bitRate
            }
        }, isClose)


        if (this.testOutputWavLog) {
            //测试输出一份wav，方便对比数据
            const recMock2 = Recorder({
                type: "wav"
                , sampleRate: this.testSampleRate
                , bitRate: 16
            });
            const chunk = Recorder.SampleData(this.realTimeSendTryWavTestBuffers, this.realTimeSendTryWavTestSampleRate, this.realTimeSendTryWavTestSampleRate);
            recMock2.mock(chunk.data, this.realTimeSendTryWavTestSampleRate);
            recMock2.stop((blob, duration) => {
                const logMsg = "No." + (number < 100 ? ("000" + number).substr(-3) : number);
                console.log(blob, duration, recMock2, logMsg);
            });
        }
        this.realTimeSendTryWavTestBuffers = [];
    }

    //=====实时处理时清理一下内存（延迟清理），本方法先于RealTimeSendTry执行======
    realTimeOnProcessClear(buffers, powerLevel, bufferDuration, bufferSampleRate, newBufferIdx, asyncEnd) {
        if (this.realTimeSendTryTime == 0) {
            this.realTimeSendTryTime = Date.now();
            this.realTimeSendTryNumber = 0;
            this.transferUploadNumberMax = 0;
            this.realTimeSendTryBytesChunks = [];
            this.realTimeSendTryClearPrevBufferIdx = 0;
            this.realTimeSendTryWavTestBuffers = [];
            this.realTimeSendTryWavTestSampleRate = 0;
        }

        //清理PCM缓冲数据，最后完成录音时不能调用stop，因为数据已经被清掉了
        //这里进行了延迟操作（必须要的操作），只清理上次到现在的buffer
        for (let i = this.realTimeSendTryClearPrevBufferIdx; i < newBufferIdx; i++) {
            buffers[i] = null;
        }
        this.realTimeSendTryClearPrevBufferIdx = newBufferIdx;

        //备份一下方便后面生成测试wav
        for (let i = newBufferIdx; i < buffers.length; i++) {
            this.realTimeSendTryWavTestBuffers.push(buffers[i]);
        }
        this.realTimeSendTryWavTestSampleRate = bufferSampleRate;
    };

    //=====数据传输函数==========
    transferUpload(number, blobOrNull, duration, blobRec, isClose) {
        this.transferUploadNumberMax = Math.max(this.transferUploadNumberMax, number);
        if (blobOrNull) {
            const blob = blobOrNull;

            //*********发送方式一：Base64文本发送***************
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64 = (/.+;\s*base64\s*,\s*(.+)$/i.exec(reader.result) || [])[1];

                if (this.dataCb && typeof this.dataCb === 'function') {
                    this.dataCb(base64)
                }
                //可以实现
                //WebSocket send(base64) ...
                //WebRTC send(base64) ...
                //XMLHttpRequest send(base64) ...

                //这里啥也不干
            };
            reader.readAsDataURL(blob);

            //*********发送方式二：Blob二进制发送***************
            //可以实现
            //WebSocket send(blob) ...
            //WebRTC send(blob) ...
            //XMLHttpRequest send(blob) ...

            //****这里仅 console.log一下 意思意思****
            const numberFail = number < this.transferUploadNumberMax ? '<span style="color:red">顺序错乱的数据，如果要求不高可以直接丢弃，或者调大SendInterval试试</span>' : "";
            const logMsg = "No." + (number < 100 ? ("000" + number).substr(-3) : number) + numberFail;
            console.log(blob, duration, blobRec, logMsg);
            if (true && number % 100 == 0) {
                console.log('clear');
            }
        }

        if (isClose) {
            console.log("No." + (number < 100 ? ("000" + number).substr(-3) : number) + ":已停止传输");
        }
    };

    mp3Merge(fileBytesList, bitRate, True) {
        //计算所有文件总长度
        let size = 0;
        for (let i = 0; i < fileBytesList.length; i++) {
            size += fileBytesList[i].byteLength;
        }

        //全部直接拼接到一起
        const fileBytes = new Uint8Array(size);
        let pos = 0;
        for (let i = 0; i < fileBytesList.length; i++) {
            const bytes = fileBytesList[i];
            fileBytes.set(bytes, pos);
            pos += bytes.byteLength;
        }

        //计算合并后的总时长
        const duration = Math.round(size * 8 / bitRate);
        if (True && typeof True === 'function') {
            True(fileBytes, duration);
        }
    }

    formatMs(ms, all) {
        const ss = ms % 1000;
        ms = (ms - ss) / 1000;
        const s = ms % 60;
        ms = (ms - s) / 60;
        const m = ms % 60;
        ms = (ms - m) / 60;
        const h = ms;
        const t = (h ? h + ":" : "")
            + (all || h + m ? ("0" + m).substr(-2) + ":" : "")
            + (all || h + m + s ? ("0" + s).substr(-2) + "″" : "")
            + ("00" + ss).substr(-3);
        return t;
    };

    //调用录音
    start() {
        if (!this.recorder || !Recorder.IsOpen()) {
            return
        }
        //开始录音
        this.recorder.start();
        //重置环境，开始录音时必须调用一次
        this.realTimeSendTryReset();
    }

    close() {
        if (!this.recorder || !Recorder.IsOpen()) {
            return
        }
        //直接close掉即可，这个例子不需要获得最终的音频文件
        this.recorder.close();
    }

    stop() {
        if (!this.recorder || !Recorder.IsOpen()) {
            return
        }
        debugger
        //最后一次发送
        this.realTimeSendTry(null, true);
        this.recorder.stop((blob, duration) => {
            console.log("0LHf::已录制mp3：{1}ms {2}字节，可以点击播放、上传、本地下载了", 0, this.formatMs(duration), blob.size, 2);
        }, function (msg) {
            console.log("kGZO::录音失败:" + msg, 1);
        });
        if (this.chunks && this.chunks.length) {
            let len = 0;
            for (let i = 0; i < this.chunks.length; i++) {
                len += this.chunks[i].length;
            }
            const chunkData = new Uint8Array(len);
            for (let i = 0, idx = 0; i < this.realTimeSendTryBytesChunks.length; i++) {
                const chunk = this.realTimeSendTryBytesChunks[i];
                chunkData.set(chunk, idx);
                idx += chunk.length;
            }
            this.chunks = [];
            if (chunkData.length > 0) {
                console.log('chunkData.length', chunkData.length)
                // const blob = new Blob([chunkData], {type: "audio/mp3"});
                // const meta = Recorder.mp3ReadMeta([chunkData.buffer], chunkData.length) || {};
                // console.log(blob, meta)
                // const audio = document.createElement("audio");
                // audio.controls = true;
                // document.querySelector('body').appendChild(audio);
                // audio.src = (window.URL || webkitURL).createObjectURL(blob);
                // audio.play();

                // 创建音频上下文
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();

                // 创建一个音频源节点
                const source = audioContext.createBufferSource();

                // 解码音频文件
                audioContext.decodeAudioData(chunkData.buffer, function (decodedData) {
                    // 将解码后的音频数据设置为音频源节点的缓冲区
                    source.buffer = decodedData;

                    // 连接音频源节点到音频输出
                    source.connect(audioContext.destination);

                    // 播放音频
                    source.start();
                });
            }
        }
    }
}

export default RecorderManager