/**
 * 音频转换工具 - 专门处理WebM到WAV的转换
 */

/**
 * 将WebM音频转换为WAV格式
 * @param {Blob} webmBlob - WebM格式的音频Blob
 * @param {number} sampleRate - 目标采样率，默认16000
 * @returns {Promise<Blob>} WAV格式的音频Blob
 */
export async function convertWebMToWav(webmBlob, sampleRate = 16000) {
  return new Promise((resolve, reject) => {
    try {
      // 创建AudioContext
      const audioContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: sampleRate
      })
      
      const fileReader = new FileReader()
      
      fileReader.onload = async (e) => {
        try {
          console.log('开始解码WebM音频数据...')
          const arrayBuffer = e.target.result
          
          // 解码音频数据
          const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
          console.log('音频解码成功:', {
            sampleRate: audioBuffer.sampleRate,
            channels: audioBuffer.numberOfChannels,
            duration: audioBuffer.duration
          })
          
          // 转换为WAV
          const wavBlob = audioBufferToWav(audioBuffer, sampleRate)
          console.log('WAV转换完成，大小:', wavBlob.size)
          
          resolve(wavBlob)
        } catch (error) {
          console.error('音频解码失败:', error)
          reject(new Error(`音频解码失败: ${error.message}`))
        }
      }
      
      fileReader.onerror = () => {
        reject(new Error('文件读取失败'))
      }
      
      fileReader.readAsArrayBuffer(webmBlob)
    } catch (error) {
      console.error('音频转换初始化失败:', error)
      reject(error)
    }
  })
}

/**
 * 将AudioBuffer转换为WAV格式的Blob
 * @param {AudioBuffer} audioBuffer - 音频缓冲区
 * @param {number} targetSampleRate - 目标采样率
 * @returns {Blob} WAV格式的Blob
 */
function audioBufferToWav(audioBuffer, targetSampleRate = 16000) {
  const numChannels = 1 // 强制单声道
  const sampleRate = targetSampleRate
  const format = 1 // PCM
  const bitDepth = 16
  
  // 获取音频数据并重采样
  let audioData
  if (audioBuffer.numberOfChannels === 1) {
    // 单声道，直接使用
    audioData = audioBuffer.getChannelData(0)
  } else {
    // 多声道，混合为单声道
    const left = audioBuffer.getChannelData(0)
    const right = audioBuffer.numberOfChannels > 1 ? audioBuffer.getChannelData(1) : left
    audioData = new Float32Array(left.length)
    for (let i = 0; i < left.length; i++) {
      audioData[i] = (left[i] + right[i]) / 2
    }
  }
  
  // 重采样到目标采样率
  if (audioBuffer.sampleRate !== targetSampleRate) {
    audioData = resampleAudio(audioData, audioBuffer.sampleRate, targetSampleRate)
  }
  
  const length = audioData.length
  const bytesPerSample = bitDepth / 8
  const blockAlign = numChannels * bytesPerSample
  const byteRate = sampleRate * blockAlign
  const dataSize = length * bytesPerSample
  const bufferSize = 44 + dataSize
  
  const arrayBuffer = new ArrayBuffer(bufferSize)
  const view = new DataView(arrayBuffer)
  
  // WAV文件头
  let offset = 0
  
  // RIFF chunk descriptor
  writeString(view, offset, 'RIFF'); offset += 4
  view.setUint32(offset, bufferSize - 8, true); offset += 4
  writeString(view, offset, 'WAVE'); offset += 4
  
  // fmt sub-chunk
  writeString(view, offset, 'fmt '); offset += 4
  view.setUint32(offset, 16, true); offset += 4 // Sub-chunk size
  view.setUint16(offset, format, true); offset += 2 // Audio format (PCM)
  view.setUint16(offset, numChannels, true); offset += 2 // Number of channels
  view.setUint32(offset, sampleRate, true); offset += 4 // Sample rate
  view.setUint32(offset, byteRate, true); offset += 4 // Byte rate
  view.setUint16(offset, blockAlign, true); offset += 2 // Block align
  view.setUint16(offset, bitDepth, true); offset += 2 // Bits per sample
  
  // data sub-chunk
  writeString(view, offset, 'data'); offset += 4
  view.setUint32(offset, dataSize, true); offset += 4
  
  // 写入音频数据
  for (let i = 0; i < length; i++) {
    const sample = Math.max(-1, Math.min(1, audioData[i]))
    const intSample = Math.round(sample * 0x7FFF)
    view.setInt16(offset, intSample, true)
    offset += 2
  }
  
  const wavBlob = new Blob([arrayBuffer], { type: 'audio/wav' })
  
  // 验证生成的WAV文件
  console.log('生成WAV文件:', {
    size: wavBlob.size,
    type: wavBlob.type,
    sampleRate: sampleRate,
    channels: numChannels,
    samples: length
  })
  
  return wavBlob
}

/**
 * 音频重采样
 * @param {Float32Array} audioData - 原始音频数据
 * @param {number} originalSampleRate - 原始采样率
 * @param {number} targetSampleRate - 目标采样率
 * @returns {Float32Array} 重采样后的音频数据
 */
function resampleAudio(audioData, originalSampleRate, targetSampleRate) {
  if (originalSampleRate === targetSampleRate) {
    return audioData
  }
  
  const ratio = originalSampleRate / targetSampleRate
  const newLength = Math.round(audioData.length / ratio)
  const result = new Float32Array(newLength)
  
  for (let i = 0; i < newLength; i++) {
    const originalIndex = i * ratio
    const index = Math.floor(originalIndex)
    const fraction = originalIndex - index
    
    if (index + 1 < audioData.length) {
      // 线性插值
      result[i] = audioData[index] * (1 - fraction) + audioData[index + 1] * fraction
    } else {
      result[i] = audioData[index] || 0
    }
  }
  
  console.log(`重采样: ${originalSampleRate}Hz -> ${targetSampleRate}Hz, ${audioData.length} -> ${newLength} samples`)
  return result
}

/**
 * 写入字符串到DataView
 * @param {DataView} view - DataView对象
 * @param {number} offset - 偏移量
 * @param {string} string - 要写入的字符串
 */
function writeString(view, offset, string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i))
  }
}

/**
 * 检测音频是否需要转换
 * @param {string} mimeType - 音频MIME类型
 * @returns {boolean} 是否需要转换
 */
export function needsConversion(mimeType) {
  return mimeType.includes('webm') || mimeType.includes('opus') || mimeType.includes('ogg')
}

/**
 * 获取音频基本信息
 * @param {Blob} audioBlob - 音频Blob
 * @returns {Promise<Object>} 音频信息
 */
export async function getAudioInfo(audioBlob) {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    const arrayBuffer = await audioBlob.arrayBuffer()
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
    
    return {
      sampleRate: audioBuffer.sampleRate,
      channels: audioBuffer.numberOfChannels,
      duration: audioBuffer.duration,
      samples: audioBuffer.length
    }
  } catch (error) {
    console.error('获取音频信息失败:', error)
    return null
  }
}
