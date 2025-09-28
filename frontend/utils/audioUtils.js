/**
 * 音频处理工具函数
 */

/**
 * 将音频Blob转换为WAV格式
 * @param {Blob} audioBlob - 原始音频Blob
 * @param {number} sampleRate - 采样率，默认16000
 * @returns {Promise<Blob>} WAV格式的音频Blob
 */
export async function convertToWav(audioBlob, sampleRate = 16000) {
  return new Promise((resolve, reject) => {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: sampleRate
      })
      
      const fileReader = new FileReader()
      
      fileReader.onload = async (e) => {
        try {
          const arrayBuffer = e.target.result
          const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
          
          // 转换为WAV格式
          const wavBlob = audioBufferToWav(audioBuffer)
          resolve(wavBlob)
        } catch (error) {
          console.error('音频解码失败:', error)
          reject(error)
        }
      }
      
      fileReader.onerror = () => {
        reject(new Error('文件读取失败'))
      }
      
      fileReader.readAsArrayBuffer(audioBlob)
    } catch (error) {
      console.error('音频转换失败:', error)
      reject(error)
    }
  })
}

/**
 * 将AudioBuffer转换为WAV格式的Blob
 * @param {AudioBuffer} audioBuffer - 音频缓冲区
 * @returns {Blob} WAV格式的Blob
 */
function audioBufferToWav(audioBuffer) {
  const numChannels = audioBuffer.numberOfChannels
  const sampleRate = audioBuffer.sampleRate
  const format = 1 // PCM
  const bitDepth = 16
  
  const bytesPerSample = bitDepth / 8
  const blockAlign = numChannels * bytesPerSample
  
  const buffer = audioBuffer.getChannelData(0)
  const length = buffer.length
  const arrayBuffer = new ArrayBuffer(44 + length * bytesPerSample)
  const view = new DataView(arrayBuffer)
  
  // WAV文件头
  const writeString = (offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i))
    }
  }
  
  let offset = 0
  
  // RIFF chunk descriptor
  writeString(offset, 'RIFF'); offset += 4
  view.setUint32(offset, 36 + length * bytesPerSample, true); offset += 4
  writeString(offset, 'WAVE'); offset += 4
  
  // fmt sub-chunk
  writeString(offset, 'fmt '); offset += 4
  view.setUint32(offset, 16, true); offset += 4 // Sub-chunk size
  view.setUint16(offset, format, true); offset += 2 // Audio format
  view.setUint16(offset, numChannels, true); offset += 2 // Number of channels
  view.setUint32(offset, sampleRate, true); offset += 4 // Sample rate
  view.setUint32(offset, sampleRate * blockAlign, true); offset += 4 // Byte rate
  view.setUint16(offset, blockAlign, true); offset += 2 // Block align
  view.setUint16(offset, bitDepth, true); offset += 2 // Bits per sample
  
  // data sub-chunk
  writeString(offset, 'data'); offset += 4
  view.setUint32(offset, length * bytesPerSample, true); offset += 4
  
  // 写入音频数据
  const volume = 1
  let index = offset
  for (let i = 0; i < length; i++) {
    const sample = Math.max(-1, Math.min(1, buffer[i]))
    view.setInt16(index, sample * (0x7FFF * volume), true)
    index += 2
  }
  
  return new Blob([arrayBuffer], { type: 'audio/wav' })
}

/**
 * 检测音频格式
 * @param {Blob} audioBlob - 音频Blob
 * @returns {Promise<string>} 音频格式
 */
export async function detectAudioFormat(audioBlob) {
  return new Promise((resolve) => {
    const reader = new FileReader()
    
    reader.onload = (e) => {
      const arrayBuffer = e.target.result
      const uint8Array = new Uint8Array(arrayBuffer)
      
      // 检查文件头
      if (uint8Array.length >= 12) {
        // WAV格式检查
        if (uint8Array[0] === 0x52 && uint8Array[1] === 0x49 && 
            uint8Array[2] === 0x46 && uint8Array[3] === 0x46) {
          resolve('wav')
          return
        }
        
        // WebM格式检查
        if (uint8Array[0] === 0x1a && uint8Array[1] === 0x45 && 
            uint8Array[2] === 0xdf && uint8Array[3] === 0xa3) {
          resolve('webm')
          return
        }
        
        // MP3格式检查
        if ((uint8Array[0] === 0xFF && (uint8Array[1] & 0xE0) === 0xE0) ||
            (uint8Array[0] === 0x49 && uint8Array[1] === 0x44 && uint8Array[2] === 0x33)) {
          resolve('mp3')
          return
        }
      }
      
      // 默认返回未知格式
      resolve('unknown')
    }
    
    reader.onerror = () => resolve('unknown')
    reader.readAsArrayBuffer(audioBlob.slice(0, 12))
  })
}

