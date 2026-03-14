import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateStr) {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function getInitials(email) {
  if (!email) return '?';
  return email.charAt(0).toUpperCase();
}

export function getProgramLabel(value) {
  const labels = {
    'BSCSE': 'BSc in Computer Science & Engineering',
    'BSEEE': 'BSc in Electrical & Electronic Engineering',
    'LLB': 'LLB Honors'
  };
  return labels[value] || value;
}

export function getAuditLevelLabel(value) {
  const labels = {
    1: 'Level 1 - Credit Tally',
    2: 'Level 2 - CGPA Calculation',
    3: 'Level 3 - Full Graduation Check'
  };
  return labels[value] || `Level ${value}`;
}
