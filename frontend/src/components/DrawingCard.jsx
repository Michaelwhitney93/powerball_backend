function formatAlgorithm(name) {
  return name
    .replace(/_constrained$/, '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
}

function Ball({ number, isPowerball }) {
  return (
    <div className={isPowerball ? 'ball powerball' : 'ball whiteball'}>
      {number}
    </div>
  );
}

export default function DrawingCard({ drawing, onRegenerate, onToggleLock, loading }) {
  const { white_balls, power_ball, algorithm, locked } = drawing;

  return (
    <div className={`drawing-card ${locked ? 'locked' : ''}`}>
      <div className="balls">
        {white_balls.map((n, i) => (
          <Ball key={i} number={n} isPowerball={false} />
        ))}
        <Ball number={power_ball} isPowerball={true} />
      </div>
      <div className="algorithm-name">{formatAlgorithm(algorithm)}</div>
      <div className="card-actions">
        <button
          className={`btn-lock ${locked ? 'btn-lock--locked' : ''}`}
          onClick={onToggleLock}
          title={locked ? 'Unlock' : 'Lock'}
        >
          {locked ? '🔒 Locked' : '🔓 Lock'}
        </button>
        <button
          className="btn-regenerate"
          onClick={onRegenerate}
          disabled={locked || loading}
          title="Regenerate this drawing"
        >
          ↻ Regenerate
        </button>
      </div>
    </div>
  );
}
