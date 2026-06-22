export async function generateDrawings(count) {
  const res = await fetch(`/generate/powerball/multi?drawings=${count}`);
  if (!res.ok) throw new Error('Failed to generate drawings');
  const data = await res.json();
  return data.generations;
}

export async function saveGenerations(generations) {
  const res = await fetch('/generate/powerball/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ generations }),
  });
  if (!res.ok) throw new Error('Failed to save generations');
  return res.json();
}
