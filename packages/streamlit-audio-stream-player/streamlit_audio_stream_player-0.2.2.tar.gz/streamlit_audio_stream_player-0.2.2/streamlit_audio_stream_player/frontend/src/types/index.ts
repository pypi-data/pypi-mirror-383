/**
 * Common types for audio visualizers
 */

/**
 * Agent state for bar visualizer
 */
export type BarAgentState =
  | "connecting"
  | "initializing"
  | "listening"
  | "speaking"
  | "thinking"

/**
 * Agent state for orb visualizer
 */
export type OrbAgentState = null | "thinking" | "listening" | "talking"

/**
 * Audio analyser configuration options
 */
export interface AudioAnalyserOptions {
  fftSize?: number
  smoothingTimeConstant?: number
  minDecibels?: number
  maxDecibels?: number
}

/**
 * Multiband volume analysis options
 */
export interface MultiBandVolumeOptions {
  bands?: number
  loPass?: number // Low frequency cutoff
  hiPass?: number // High frequency cutoff
  updateInterval?: number // Update interval in ms
  analyserOptions?: AudioAnalyserOptions
}

