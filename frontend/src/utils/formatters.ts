export function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'Just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

export function getScoreColorClass(score: number): string {
  if (score >= 0.85) return 'text-success';
  if (score >= 0.70) return 'text-warning';
  return 'text-danger';
}

export function getScoreBgClass(score: number): string {
  if (score >= 0.85) return 'bg-success';
  if (score >= 0.70) return 'bg-warning';
  return 'bg-danger';
}
