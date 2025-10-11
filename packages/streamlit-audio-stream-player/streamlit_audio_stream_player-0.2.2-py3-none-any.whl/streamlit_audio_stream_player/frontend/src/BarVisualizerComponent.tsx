import React, { createRef } from "react"
import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import { BarVisualizer } from "./components/visualizers/bar-visualizer"
import { OrbVisualizer } from "./components/visualizers/orb-visualizer"
import type { BarAgentState, OrbAgentState } from "./types"
import "./index.css"

type AudioState = "loading" | "playing" | "ended" | "idle"

interface State {
  mediaStream: MediaStream | null
  audioState: AudioState
  audioVolume: number
}

class BarVisualizerComponent extends StreamlitComponentBase<State> {
  public state: State = { mediaStream: null, audioState: "idle", audioVolume: 0 }
  private audioRef = createRef<HTMLAudioElement>()
  private analyzerRef: AnalyserNode | null = null
  private audioContextRef: AudioContext | null = null
  private animationFrameId: number | null = null

  public render = (): React.ReactNode => {
    const mode = this.props.args["mode"] || "bar"
    const barCount = this.props.args["barCount"] || 20
    const minHeight = this.props.args["minHeight"] || 15
    const maxHeight = this.props.args["maxHeight"] || 90
    const centerAlign = this.props.args["centerAlign"] || false
    const streamUrl = this.props.args["streamUrl"]
    const barColor = this.props.args["barColor"] || "#3b82f6"
    const backgroundColor = this.props.args["backgroundColor"] || "#f1f5f9"
    const orbColors = this.props.args["orbColors"] || ["#CADCFC", "#A0B9D1"]
    const orbSeed = this.props.args["orbSeed"] || 1000

    // 檢查必填參數
    if (!streamUrl) {
      return (
        <div className="streamlit-bar-visualizer" style={{ padding: "20px", color: "red" }}>
          ❌ Error: stream_url is required
        </div>
      )
    }

    // state 固定為 auto：根據音頻狀態自動切換顯示
    // Bar 模式: loading → thinking, playing → speaking, ended → initializing
    // Orb 模式: loading → listening, playing → talking, ended → idle (null)
    let barDisplayState: BarAgentState
    let orbDisplayState: OrbAgentState
    
    switch (this.state.audioState) {
      case "loading":
        // 還沒獲取到首包音檔
        barDisplayState = "thinking"
        orbDisplayState = "listening"
        break
      case "playing":
        // 播放使用中
        barDisplayState = "speaking"
        orbDisplayState = "talking"
        break
      case "ended":
        // 播放完畢
        barDisplayState = "initializing"
        orbDisplayState = null  // idle state
        break
      case "idle":
      default:
        barDisplayState = "listening"
        orbDisplayState = "thinking"  // ElevenLabs orb uses "thinking" for idle
        break
    }
    console.log("🤖 Auto mode: audioState =", this.state.audioState, "→ displayState =", mode === "orb" ? orbDisplayState : barDisplayState)

    return (
      <div className="streamlit-bar-visualizer">
        <audio
          ref={this.audioRef}
          controls={false}
          autoPlay={false}
          crossOrigin="anonymous"
          style={{ display: "none" }}
        />
        {mode === "orb" ? (
          <div
            className="relative h-32 w-32 mx-auto rounded-full p-1 shadow-[inset_0_2px_8px_rgba(0,0,0,0.1)]"
            style={{ backgroundColor }}
          >
            <div className="h-full w-full overflow-hidden rounded-full shadow-[inset_0_0_12px_rgba(0,0,0,0.05)]">
              <OrbVisualizer
                colors={orbColors as [string, string]}
                seed={orbSeed}
                agentState={orbDisplayState}
                volumeMode="manual"
                manualOutput={this.state.audioVolume}
              />
            </div>
          </div>
        ) : (
          <BarVisualizer
            mediaStream={this.state.mediaStream}
            state={barDisplayState}
            barCount={barCount}
            minHeight={minHeight}
            maxHeight={maxHeight}
            centerAlign={centerAlign}
            barColor={barColor}
            backgroundColor={backgroundColor}
          />
        )}
      </div>
    )
  }

  public componentDidMount = async (): Promise<void> => {
    const streamUrl = this.props.args["streamUrl"]
    
    if (!streamUrl || !this.audioRef.current) {
      Streamlit.setFrameHeight()
      return
    }

    console.log("🎵 Attempting to load audio stream:", streamUrl)
    const audioEl = this.audioRef.current
    
    // Force reload by setting src explicitly and calling load()
    // This ensures audio loads even on page refresh with same URL
    audioEl.src = streamUrl
    audioEl.load()
    
    // 設置音頻狀態為 loading
    this.setState({ audioState: "loading" })
    
    // 添加音頻事件監聽器
    audioEl.addEventListener("loadstart", this.handleLoadStart)
    audioEl.addEventListener("playing", this.handlePlaying)
    audioEl.addEventListener("ended", this.handleEnded)
    
    try {
      // Wait for audio to be ready
      await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error("Audio load timeout")), 10000)
        
        audioEl.oncanplay = () => {
          clearTimeout(timeout)
          resolve(true)
        }
        
        audioEl.onerror = (e: any) => {
          clearTimeout(timeout)
          console.error("❌ Audio element error event:", e)
          console.error("   Error code:", audioEl.error?.code)
          console.error("   Error message:", audioEl.error?.message)
          console.error("   Network state:", audioEl.networkState)
          console.error("   Ready state:", audioEl.readyState)
          reject(new Error(`Audio load error: ${audioEl.error?.message || 'Unknown error'}`))
        }
      })

      // Try to play the audio (muted first to bypass autoplay restrictions)
      audioEl.muted = true
      await audioEl.play()
      console.log("✅ Audio stream is playing (initially muted)")

      // Small delay to ensure audio context is ready
      await new Promise(resolve => setTimeout(resolve, 100))

      // Capture the stream and setup audio analysis
      const audioElAny = audioEl as any
      if (typeof audioElAny.captureStream === "function") {
        const mediaStream = audioElAny.captureStream()
        this.setState({ mediaStream })
        console.log("✅ Audio stream captured successfully via captureStream()")
        
        // Setup audio analysis for orb visualization
        this.setupAudioAnalysis(mediaStream)
        
        // Unmute after successful capture so user can hear the audio
        audioEl.muted = false
        console.log("🔊 Audio unmuted - you should now hear the sound")
      } else if (typeof audioElAny.mozCaptureStream === "function") {
        // Firefox compatibility
        const mediaStream = audioElAny.mozCaptureStream()
        this.setState({ mediaStream })
        console.log("✅ Audio stream captured successfully via mozCaptureStream() (Firefox)")
        
        // Setup audio analysis for orb visualization
        this.setupAudioAnalysis(mediaStream)
        
        // Unmute after successful capture
        audioEl.muted = false
        console.log("🔊 Audio unmuted - you should now hear the sound")
      } else {
        console.error("❌ HTMLAudioElement.captureStream() is not supported in this browser.")
        // Still unmute so user can hear the audio even without visualization
        audioEl.muted = false
        console.warn("⚠️ Audio unmuted but visualization will not work")
      }
    } catch (error) {
      console.error("❌ Error playing or capturing audio stream:", error)
      console.warn("⚠️ Audio stream failed. Check console for errors.")
    }
    
    Streamlit.setFrameHeight()
  }

  public componentWillUnmount = (): void => {
    // Clean up audio analysis
    this.cleanupAudioAnalysis()
    
    // Stop microphone tracks
    if (this.state.mediaStream && !this.props.args["streamUrl"]) {
      this.state.mediaStream.getTracks().forEach((track) => track.stop())
    }
    // Stop audio element and remove event listeners
    if (this.audioRef.current) {
      const audioEl = this.audioRef.current
      audioEl.pause()
      audioEl.removeEventListener("loadstart", this.handleLoadStart)
      audioEl.removeEventListener("playing", this.handlePlaying)
      audioEl.removeEventListener("ended", this.handleEnded)
    }
  }

  // @ts-expect-error - StreamlitComponentBase typing issue with componentDidUpdate params
  public componentDidUpdate(
    prevProps: Readonly<BarVisualizerComponent["props"]>
  ): void {
    const oldStreamUrl = prevProps.args["streamUrl"]
    const newStreamUrl = this.props.args["streamUrl"]

    // 當有 streamUrl 時，檢查是否需要重新加載音頻
    // 只在 URL 改變時重新加載，避免音頻結束後自動循環播放
    const urlChanged = oldStreamUrl !== newStreamUrl
    const shouldReload = newStreamUrl && this.audioRef.current && urlChanged

    if (shouldReload) {
      console.log("🔄 Reloading audio:", urlChanged ? "URL changed" : "Replay same URL")
      
      // 先清除 mediaStream 並設置為 loading 狀態
      this.setState({ mediaStream: null, audioState: "loading" })
      
      const audioEl = this.audioRef.current
      if (!audioEl) return
      
      // 移除舊的事件監聽器（如果有）
      audioEl.removeEventListener("loadstart", this.handleLoadStart)
      audioEl.removeEventListener("playing", this.handlePlaying)
      audioEl.removeEventListener("ended", this.handleEnded)
      
      // 添加新的事件監聽器
      audioEl.addEventListener("loadstart", this.handleLoadStart)
      audioEl.addEventListener("playing", this.handlePlaying)
      audioEl.addEventListener("ended", this.handleEnded)
      
      // 如果 URL 改變了，更新 src；否則只需要重新 load
      if (urlChanged) {
        audioEl.src = newStreamUrl
      } else {
        audioEl.load() // 重新加載相同的 URL
      }
      
      // Use async IIFE to handle async operations
      ;(async () => {
        try {
          audioEl.muted = true
          await audioEl.play()
          
          const audioElAny = audioEl as any
          if (typeof audioElAny.captureStream === "function") {
            const mediaStream = audioElAny.captureStream()
            this.setState({ mediaStream })
            console.log("✅ Audio stream updated and captured successfully")
            
            // Setup audio analysis for orb visualization
            this.setupAudioAnalysis(mediaStream)
            
            // Unmute so user can hear the audio
            audioEl.muted = false
            console.log("🔊 Audio unmuted")
          } else if (typeof audioElAny.mozCaptureStream === "function") {
            const mediaStream = audioElAny.mozCaptureStream()
            this.setState({ mediaStream })
            console.log("✅ Audio stream updated and captured successfully (Firefox)")
            
            // Setup audio analysis for orb visualization
            this.setupAudioAnalysis(mediaStream)
            
            // Unmute so user can hear the audio
            audioEl.muted = false
            console.log("🔊 Audio unmuted")
          } else {
            // Still unmute even if capture is not supported
            audioEl.muted = false
            console.warn("⚠️ captureStream not supported, audio unmuted but using demo visualization")
          }
        } catch (error) {
          console.error("❌ Error updating audio stream:", error)
        }
      })()
    }

    Streamlit.setFrameHeight()
  }

  // 事件處理器方法（使用箭頭函數保持 this 綁定）
  private handleLoadStart = () => {
    console.log("📥 Audio loadstart")
    this.setState({ audioState: "loading" })
  }

  private handlePlaying = () => {
    console.log("▶️ Audio playing")
    this.setState({ audioState: "playing" })
  }

  private handleEnded = () => {
    console.log("⏹️ Audio ended")
    // 清除 mediaStream，讓可視化停止
    this.setState({ audioState: "ended", mediaStream: null, audioVolume: 0 })
    // Clean up audio analysis
    this.cleanupAudioAnalysis()
  }

  // Setup audio analysis for volume tracking
  private setupAudioAnalysis = (mediaStream: MediaStream): void => {
    // Clean up any existing analysis first
    this.cleanupAudioAnalysis()

    try {
      const audioContext = new AudioContext()
      const analyzer = audioContext.createAnalyser()
      analyzer.fftSize = 256
      analyzer.smoothingTimeConstant = 0.8
      
      const source = audioContext.createMediaStreamSource(mediaStream)
      source.connect(analyzer)
      
      this.audioContextRef = audioContext
      this.analyzerRef = analyzer

      const dataArray = new Uint8Array(analyzer.frequencyBinCount)

      const updateVolume = () => {
        if (!this.analyzerRef) return
        
        this.analyzerRef.getByteFrequencyData(dataArray)
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length
        const normalizedVolume = Math.min(1, average / 128) // Normalize to 0-1 range
        
        this.setState({ audioVolume: normalizedVolume })
        this.animationFrameId = requestAnimationFrame(updateVolume)
      }

      updateVolume()
      console.log("✅ Audio analysis setup complete")
    } catch (error) {
      console.error("❌ Error setting up audio analysis:", error)
    }
  }

  // Clean up audio analysis resources
  private cleanupAudioAnalysis = (): void => {
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId)
      this.animationFrameId = null
    }
    
    if (this.audioContextRef) {
      this.audioContextRef.close()
      this.audioContextRef = null
    }
    
    this.analyzerRef = null
  }
}

export default withStreamlitConnection(BarVisualizerComponent)

