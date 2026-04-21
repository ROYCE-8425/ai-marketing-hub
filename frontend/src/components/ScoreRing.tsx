import { useEffect, useRef } from "react";

interface ScoreRingProps {
  score: number; // 0-100
  grade: string;
}

const RADIUS = 60;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

function scoreColor(score: number): string {
  if (score >= 80) return "#10b981"; // emerald
  if (score >= 60) return "#f59e0b"; // amber
  return "#ef4444"; // red
}

export function ScoreRing({ score, grade }: ScoreRingProps) {
  const circleRef = useRef<SVGCircleElement>(null);

  useEffect(() => {
    const el = circleRef.current;
    if (!el) return;
    const offset = CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE;
    el.style.transition = "stroke-dashoffset 1.2s cubic-bezier(0.34, 1.56, 0.64, 1)";
    el.style.strokeDashoffset = String(offset);
  }, [score]);

  const color = scoreColor(score);

  return (
    <div className="score-ring-wrapper">
      <svg viewBox="0 0 160 160" width="160" height="160" aria-label={`SEO Score ${score}`}>
        {/* Track */}
        <circle
          cx="80"
          cy="80"
          r={RADIUS}
          fill="none"
          stroke="#1e293b"
          strokeWidth="10"
        />
        {/* Progress */}
        <circle
          ref={circleRef}
          cx="80"
          cy="80"
          r={RADIUS}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={CIRCUMFERENCE}
          transform="rotate(-90 80 80)"
          style={{ filter: `drop-shadow(0 0 8px ${color}80)` }}
        />
        {/* Score text */}
        <text
          x="80"
          y="75"
          textAnchor="middle"
          fill={color}
          fontSize="36"
          fontWeight="700"
          fontFamily="'DM Sans', sans-serif"
        >
          {score}
        </text>
        <text
          x="80"
          y="96"
          textAnchor="middle"
          fill="#94a3b8"
          fontSize="13"
          fontWeight="500"
          fontFamily="'DM Sans', sans-serif"
        >
          {grade}
        </text>
      </svg>
    </div>
  );
}
