import * as React from "react"
import { cn } from "../../lib/utils"
import { useMultibandVolume } from "../../hooks/use-audio-analysis"
import { useBarAnimator } from "../../hooks/use-bar-animator"
import type { BarAgentState } from "../../types"

export interface BarVisualizerProps
  extends React.HTMLAttributes<HTMLDivElement> {
  /** Voice assistant state */
  state?: BarAgentState
  /** Number of bars to display */
  barCount?: number
  /** Audio source */
  mediaStream?: MediaStream | null
  /** Min/max height as percentage */
  minHeight?: number
  maxHeight?: number
  /** Align bars from center instead of bottom */
  centerAlign?: boolean
  /** Color of the bars */
  barColor?: string
  /** Background color */
  backgroundColor?: string
}

const BarVisualizerComponent = React.forwardRef<
  HTMLDivElement,
  BarVisualizerProps
>(
  (
    {
      state,
      barCount = 15,
      mediaStream,
      minHeight = 20,
      maxHeight = 100,
      centerAlign = false,
      barColor = "#3b82f6",
      backgroundColor = "#f1f5f9",
      className,
      style,
      ...props
    },
    ref
  ) => {
    // Audio processing - 只使用真實音頻數據
    const realVolumeBands = useMultibandVolume(mediaStream, {
      bands: barCount,
      loPass: 100,
      hiPass: 200,
    })
    
    // 當狀態為 initializing 時，重置所有條形圖高度為 0
    const volumeBands = state === "initializing" 
      ? new Array(barCount).fill(0) 
      : realVolumeBands

    // Animation sequencing
    const highlightedIndices = useBarAnimator(
      state,
      barCount,
      state === "connecting"
        ? 2000 / barCount
        : state === "thinking"
          ? 150
          : state === "listening"
            ? 500
            : 1000
    )

    return (
      <div
        ref={ref}
        data-state={state}
        className={cn(
          "relative flex justify-center gap-1.5",
          centerAlign ? "items-center" : "items-end",
          "h-28 w-full overflow-hidden rounded-lg",
          className
        )}
        style={{
          backgroundColor,
          ...style,
        }}
        {...props}
      >
        {volumeBands.map((volume, index) => {
          const heightPct = Math.min(
            maxHeight,
            Math.max(minHeight, volume * 100 + 5)
          )
          const isHighlighted = highlightedIndices?.includes(index) ?? false

          return (
            <Bar
              key={index}
              heightPct={heightPct}
              isHighlighted={isHighlighted}
              state={state}
              barColor={barColor}
            />
          )
        })}
      </div>
    )
  }
)

// Memoized Bar component to prevent unnecessary re-renders
const Bar = React.memo<{
  heightPct: number
  isHighlighted: boolean
  state?: BarAgentState
  barColor?: string
}>(({ heightPct, isHighlighted, state, barColor = "#3b82f6" }) => {
  // Determine bar color based on state
  const getBarColor = () => {
    if (state === "speaking") return barColor
    if (isHighlighted) return barColor
    // Lighter/dimmed version for non-highlighted bars
    return `${barColor}40` // Add 40 for 25% opacity
  }

  return (
    <div
      data-highlighted={isHighlighted}
      className={cn(
        "max-w-[12px] min-w-[8px] flex-1 transition-all duration-150",
        "rounded-full",
        state === "thinking" && isHighlighted && "animate-pulse"
      )}
      style={{
        height: `${heightPct}%`,
        backgroundColor: getBarColor(),
        animationDuration: state === "thinking" ? "300ms" : undefined,
      }}
    />
  )
})

Bar.displayName = "Bar"

// Wrap the main component with React.memo for prop comparison optimization
const BarVisualizer = React.memo(
  BarVisualizerComponent,
  (prevProps, nextProps) => {
    return (
      prevProps.state === nextProps.state &&
      prevProps.barCount === nextProps.barCount &&
      prevProps.mediaStream === nextProps.mediaStream &&
      prevProps.minHeight === nextProps.minHeight &&
      prevProps.maxHeight === nextProps.maxHeight &&
      prevProps.centerAlign === nextProps.centerAlign &&
      prevProps.barColor === nextProps.barColor &&
      prevProps.backgroundColor === nextProps.backgroundColor &&
      prevProps.className === nextProps.className &&
      JSON.stringify(prevProps.style) === JSON.stringify(nextProps.style)
    )
  }
)

BarVisualizerComponent.displayName = "BarVisualizerComponent"
BarVisualizer.displayName = "BarVisualizer"

export { BarVisualizer }

